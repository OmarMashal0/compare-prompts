"""
LLM runner — calls LiteLLM for each prompt+input combination.

Supports synchronous execution (default) and async execution
for faster parallel runs when many combinations are needed.
"""

import asyncio
import os
import litellm
from dotenv import load_dotenv

load_dotenv()

# Suppress LiteLLM's verbose debug logging
litellm.suppress_debug_info = True
os.environ.setdefault("LITELLM_LOG", "ERROR")


def run_prompt(system_prompt: str, user_input: str, model: str) -> dict:
    """
    Run a single prompt+input combination through LiteLLM.
    Returns the output text and token usage.

    Raises a clear error if the API key is missing or the model name is wrong.
    """
    try:
        response = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )

        output_text = response.choices[0].message.content or ""

        # Token usage from LiteLLM response
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens

        # Cost calculation using LiteLLM's built-in cost function
        try:
            cost = litellm.completion_cost(completion_response=response)
        except Exception:
            cost = 0.0  # fallback if model pricing not available

        return {
            "text": output_text,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost": cost,
        }

    except litellm.AuthenticationError:
        raise ValueError(
            f"\n❌ API key missing or invalid for model '{model}'.\n"
            f"   Make sure you have the right key in your .env file.\n"
            f"   See .env.example for the format.\n"
            f"\n   Common keys:\n"
            f"     OpenAI:    OPENAI_API_KEY=sk-...\n"
            f"     Anthropic: ANTHROPIC_API_KEY=sk-ant-...\n"
            f"     Gemini:    GEMINI_API_KEY=...\n"
            f"     Groq:      GROQ_API_KEY=gsk_...\n"
        )
    except litellm.BadRequestError as e:
        raise ValueError(
            f"\n❌ Model '{model}' not recognized.\n"
            f"   Check the full list at https://models.litellm.ai\n"
            f"\n   Common model strings:\n"
            f"     OpenAI:    gpt-4o-mini, gpt-4o\n"
            f"     Anthropic: claude-haiku-4-5, claude-sonnet-4-6\n"
            f"     Gemini:    gemini/gemini-2.0-flash\n"
            f"     Groq:      groq/llama-3.3-70b-versatile\n"
            f"     Ollama:    ollama/llama3\n"
            f"\n   Original error: {e}"
        )
    except litellm.RateLimitError:
        raise ValueError(
            f"\n⏳ Rate limit hit for model '{model}'.\n"
            f"   Wait a minute and try again, or reduce the number of inputs.\n"
            f"   If using Groq free tier, the limit is ~30 requests/minute.\n"
        )
    except Exception as e:
        raise ValueError(
            f"\n❌ Unexpected error calling model '{model}': {e}\n"
            f"   Check your internet connection and API key.\n"
        )


async def _run_prompt_async(
    system_prompt: str, user_input: str, model: str, semaphore: asyncio.Semaphore
) -> dict:
    """Run a single prompt+input combination asynchronously with rate limiting."""
    async with semaphore:
        try:
            response = await litellm.acompletion(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )

            output_text = response.choices[0].message.content or ""
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens

            try:
                cost = litellm.completion_cost(completion_response=response)
            except Exception:
                cost = 0.0

            return {
                "text": output_text,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cost": cost,
            }
        except Exception as e:
            # Return error info instead of crashing the whole batch
            return {
                "text": f"[ERROR: {e}]",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "cost": 0.0,
                "error": str(e),
            }


def run_all(prompts: dict, inputs: list, model: str, use_async: bool = False) -> dict:
    """
    Run all prompt+input combinations.

    Args:
        prompts: dict of {label: system_prompt_string}
        inputs: list of user input strings
        model: LiteLLM model string
        use_async: if True, run calls concurrently (faster for many combinations)

    Returns: dict of {label: [list of result dicts, one per input]}
    """
    total_calls = len(prompts) * len(inputs)

    if use_async:
        return _run_all_async(prompts, inputs, model, total_calls)
    else:
        return _run_all_sync(prompts, inputs, model, total_calls)


def _run_all_sync(prompts: dict, inputs: list, model: str, total_calls: int) -> dict:
    """Run all combinations synchronously with progress indicator."""
    results = {label: [] for label in prompts}
    call_count = 0

    for label, system_prompt in prompts.items():
        for user_input in inputs:
            result = run_prompt(system_prompt, user_input, model)
            results[label].append(result)
            call_count += 1
            print(f"\r  Running... {call_count}/{total_calls}", end="", flush=True)

    print()  # newline after progress
    return results


def _run_all_async(prompts: dict, inputs: list, model: str, total_calls: int) -> dict:
    """Run all combinations concurrently with asyncio."""
    # Limit concurrency to avoid rate limits (5 parallel calls max)
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
            # Convert exceptions to error dicts
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
