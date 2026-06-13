"""
LLM runner — native, 0-dependency clients for major providers.
Falls back to litellm for obscure providers if installed.
"""

import asyncio
import os
import json
import urllib.request
import urllib.error
from urllib.error import HTTPError

from dotenv import load_dotenv

load_dotenv()


def _native_openai_call(model, system_prompt, user_input, api_key, base_url="https://api.openai.com/v1/chat/completions"):
    req = urllib.request.Request(base_url, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "compare-prompts/1.0"
    }, data=json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    }).encode("utf-8"))
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return {
                "text": data["choices"][0]["message"]["content"],
                "prompt_tokens": data.get("usage", {}).get("prompt_tokens", 0),
                "completion_tokens": data.get("usage", {}).get("completion_tokens", 0),
                "cost": None
            }
    except HTTPError as e:
        err = e.read().decode()
        raise ValueError(f"\n❌ API Error: HTTP {e.code}\n{err}")


def _native_anthropic_call(model, system_prompt, user_input, api_key):
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", headers={
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
        "User-Agent": "compare-prompts/1.0"
    }, data=json.dumps({
        "model": model,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_input}],
        "max_tokens": 4096
    }).encode("utf-8"))
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return {
                "text": data["content"][0]["text"],
                "prompt_tokens": data.get("usage", {}).get("input_tokens", 0),
                "completion_tokens": data.get("usage", {}).get("output_tokens", 0),
                "cost": None
            }
    except HTTPError as e:
        err = e.read().decode()
        raise ValueError(f"\n❌ Anthropic API Error: HTTP {e.code}\n{err}")


def _native_gemini_call(model, system_prompt, user_input, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    req = urllib.request.Request(url, headers={
        "Content-Type": "application/json",
        "User-Agent": "compare-prompts/1.0"
    }, data=json.dumps({
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": user_input}]}]
    }).encode("utf-8"))
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            usage = data.get("usageMetadata", {})
            return {
                "text": text,
                "prompt_tokens": usage.get("promptTokenCount", 0),
                "completion_tokens": usage.get("candidatesTokenCount", 0),
                "cost": None
            }
    except HTTPError as e:
        err = e.read().decode()
        raise ValueError(f"\n❌ Gemini API Error: HTTP {e.code}\n{err}")


def run_prompt(system_prompt: str, user_input: str, model: str) -> dict:
    """Run a single prompt+input combination through native clients or litellm."""
    provider = model.split("/")[0] if "/" in model else "openai"
    model_name = model.split("/", 1)[1] if "/" in model else model

    if provider == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if not key: raise ValueError("Missing OPENAI_API_KEY in .env")
        result = _native_openai_call(model_name, system_prompt, user_input, key)
    
    elif provider == "groq":
        key = os.getenv("GROQ_API_KEY")
        if not key: raise ValueError("Missing GROQ_API_KEY in .env")
        result = _native_openai_call(model_name, system_prompt, user_input, key, "https://api.groq.com/openai/v1/chat/completions")
    
    elif provider == "deepseek":
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key: raise ValueError("Missing DEEPSEEK_API_KEY in .env")
        result = _native_openai_call(model_name, system_prompt, user_input, key, "https://api.deepseek.com")
    
    elif provider == "ollama":
        result = _native_openai_call(model_name, system_prompt, user_input, "dummy", "http://localhost:11434/v1/chat/completions")
    
    elif provider == "anthropic":
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key: raise ValueError("Missing ANTHROPIC_API_KEY in .env")
        result = _native_anthropic_call(model_name, system_prompt, user_input, key)
    
    elif provider == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if not key: raise ValueError("Missing GEMINI_API_KEY in .env")
        result = _native_gemini_call(model_name, system_prompt, user_input, key)
    
    else:
        # Fallback to litellm for obscure providers
        try:
            import litellm
            litellm.suppress_debug_info = True
            os.environ.setdefault("LITELLM_LOG", "ERROR")
            response = litellm.completion(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            cost = None
            try: cost = litellm.completion_cost(completion_response=response)
            except Exception: pass
            
            result = {
                "text": response.choices[0].message.content,
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else 0,
                "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else 0,
                "cost": cost
            }
        except ImportError:
            raise ValueError(f"\n⚠️ To use the advanced provider '{provider}', please install the full version:\n   pip install \"compare-prompts[all]\"\n")
        except Exception as e:
            raise ValueError(f"\n❌ Unexpected error calling model '{model}': {type(e).__name__}: {str(e)}\n   Check your internet connection and API key.\n")

    # Dynamically calculate cost if litellm is installed and cost is missing
    if result.get("cost") is None:
        try:
            import litellm
            p_cost, c_cost = litellm.cost_per_token(
                model=model, 
                prompt_tokens=result.get("prompt_tokens", 0), 
                completion_tokens=result.get("completion_tokens", 0)
            )
            result["cost"] = p_cost + c_cost
        except Exception:
            pass

    return result


async def _run_prompt_async(system_prompt: str, user_input: str, model: str, semaphore: asyncio.Semaphore) -> dict:
    """Run a single prompt+input combination asynchronously."""
    async with semaphore:
        try:
            return await asyncio.to_thread(run_prompt, system_prompt, user_input, model)
        except Exception as e:
            return {
                "text": f"[ERROR: {e}]",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "cost": 0.0,
                "error": str(e),
            }


def run_all(prompts: dict, inputs: list, model: str, use_async: bool = False) -> dict:
    """Run all prompt+input combinations."""
    total_calls = len(prompts) * len(inputs)

    if use_async:
        return _run_all_async(prompts, inputs, model, total_calls)
    else:
        return _run_all_sync(prompts, inputs, model, total_calls)


def _run_all_sync(prompts: dict, inputs: list, model: str, total_calls: int) -> dict:
    results = {label: [] for label in prompts}
    call_count = 0

    for label, system_prompt in prompts.items():
        for user_input in inputs:
            result = run_prompt(system_prompt, user_input, model)
            results[label].append(result)
            call_count += 1
            print(f"\r  Running... {call_count}/{total_calls}", end="", flush=True)

    print()
    return results


def _run_all_async(prompts: dict, inputs: list, model: str, total_calls: int) -> dict:
    semaphore = asyncio.Semaphore(5)

    async def _gather():
        tasks = {}
        for label, system_prompt in prompts.items():
            tasks[label] = []
            for user_input in inputs:
                task = _run_prompt_async(system_prompt, user_input, model, semaphore)
                tasks[label].append(task)

        results = {}
        for label, task_list in tasks.items():
            results[label] = await asyncio.gather(*task_list, return_exceptions=True)
            # Process exceptions
            processed = []
            for r in results[label]:
                if isinstance(r, Exception):
                    processed.append({
                        "text": f"[ERROR: {r}]",
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "cost": 0.0,
                        "error": str(r),
                    })
                else:
                    processed.append(r)
            results[label] = processed

        return results

    return asyncio.run(_gather())
