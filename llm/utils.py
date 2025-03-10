# from litellm import completion
import asyncio
import json
import logging
from functools import wraps

import anthropic
import together
import openai

from steps.eval.type import EvalError, EvalErrorCode

def log_error_wrapper(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as error:
            input = args[0] if args else None
            logging.error(f"""
[Error on Eval] EvalInput = {input}
    [Error Type]
    {type(error)}
    [Error]
    {error}
    [Error.args]
    {"\n".join(str(arg) for arg in error.args)}
""")
            raise error
    return wrapper

def handle_error_openai(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        while True:
            try:
                return await func(*args, **kwargs)
            
            # sleep and cotinue errors
            except (openai.RateLimitError, openai.InternalServerError, openai.APIConnectionError) as error:
                match error.code:
                    case "rate_limit_exceeded":
                        if error.message.find("tokens per min (TPM)") != -1:
                            await asyncio.sleep(60)
                        else:
                            await asyncio.sleep(1)
                        continue
                    case "insufficient_quota":
                        raise error
                    case _:
                        raise error
            # write EvalError into the pair.eval_error record
            except openai.BadRequestError as error:
                match error.code:
                    case "context_length_exceeded":
                        raise EvalError(code=EvalErrorCode.context_length_exceeded, inner_error=error)
                    case "string_above_max_length":
                        raise EvalError(code=EvalErrorCode.string_above_max_length, inner_error=error)
                    case _:
                        raise error

            # directly raise
            # except openai.AuthenticationError as error:
                # raise error
            
            # except Exception as error:
                # raise error
    return wrapper

"""
def handle_error_deepseek(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        while True:
            try:
                return await func(*args, **kwargs)
            
            # sleep and cotinue errors
            except (openai.RateLimitError, openai.InternalServerError, openai.APIConnectionError, openai.BadRequestError) as error:
                match error.code:
                    case "rate_limit_exceeded":
                        if error.message.find("tokens per min (TPM)") != -1:
                            await asyncio.sleep(60)
                        else:
                            await asyncio.sleep(1)
                        continue
                    case "insufficient_quota":
                        raise error
                    case "invalid_request_error":
                        # NOTE: Deepseek API only support 64k tokens
                        if error.message.find("This model's maximum context length is 65536 tokens") != -1:
                            print("Error: This model's maximum context length is 65536 tokens", flush=True)
                            return "Sorry, the model's maximum context length is 65536 tokens."
                    case _:
                        raise error
            # write EvalError into the pair.eval_error record
            except openai.BadRequestError as error:
                match error.code:
                    case "context_length_exceeded":
                        raise EvalError(code=EvalErrorCode.context_length_exceeded, inner_error=error)
                    case "string_above_max_length":
                        raise EvalError(code=EvalErrorCode.string_above_max_length, inner_error=error)
                    case _:
                        raise error

            # directly raise
            # except openai.AuthenticationError as error:
                # raise error
            
            # except Exception as error:
                # raise error
    return wrapper
"""

def handle_error_anthropic(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        while True:
            try:
                return await func(*args, **kwargs)
            
            except anthropic.RateLimitError as error:
                # Error code: 429 - {'type': 'error', 'error': {'type': 'rate_limit_error', 'message': 'This request would exceed your organization’s rate limit of 400,000 input tokens per minute. For details, refer to: https://docs.anthropic.com/en/api/rate-limits; see the response headers for current usage. Please reduce the prompt length or the maximum tokens requested, or try again later. You may also contact sales at https://www.anthropic.com/contact-sales to discuss your options for a rate limit increase.'}}
                match error.body["error"]["type"]:
                    case "rate_limit_error":
                        # sleep and cotinue errors
                        if error.body["error"]["message"].find("tokens per minute") != -1:
                            await asyncio.sleep(60)
                        else:
                            await asyncio.sleep(1)
                        continue
                    case _:
                        raise error

            # directly raise
            # except openai.AuthenticationError as error:
                # raise error
            
            # except Exception as error:
                # raise error
    return wrapper

def handle_error_together(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        while True:
            try:
                return await func(*args, **kwargs)
            except together.error.ServiceUnavailableError as error:
                error_message = error._message[18:]
                match(type(error), error.http_status, error_message):
                    case (together.error.ServiceUnavailableError, 503, "The server is overloaded or not ready yet."):
                        await asyncio.sleep(60)
                        continue
                    case _:
                        raise error
            except (together.error.APIError, together.error.RateLimitError) as error:
                try:
                    error_obj = json.loads(error._message[18:])
                    if error_obj["type_"] is None and error_obj["message"] == "Internal Server Error":
                        await asyncio.sleep(60)
                        continue
                    match type(error), error.http_status, error_obj["type_"],  error_obj["message"]:
                        case (together.error.RateLimitError, 429, "model_rate_limit", "You have reached the rate limit specific to this model deepseek-ai/DeepSeek-R1. The maximum rate limit for this model is 120 queries per minute. This limit differs from the general rate limits published at Together AI rate limits documentation (https://docs.together.ai/docs/rate-limits). For inquiries about increasing your model-specific rate limit, please contact our sales team (https://www.together.ai/forms/contact-sales)"):
                            await asyncio.sleep(60)
                            continue
                        case (together.error.APIError, 500, "server_error", "Internal server error"):
                            await asyncio.sleep(60)
                            continue
                        case (together.error.APIError, 413, "invalid_request_error", "Request entity too large"):
                            raise EvalError(code=EvalErrorCode.string_above_max_length, inner_error=error)
                        case _:
                            raise error
                except json.JSONDecodeError as json_error:
                    match type(error), error.http_status:
                        case (together.error.APIError, 502):
                            await asyncio.sleep(60)
                            continue
                        case _:
                            raise error
            except together.error.InvalidRequestError as error:
                error_obj = json.loads(error._message[18:])
                match type(error), error.http_status, error_obj["type_"]:
                    case (together.error.InvalidRequestError, 422, "invalid_request_error") if error_obj["message"].startswith("Input validation error: `inputs` tokens + `max_new_tokens` must be <="):
                        # write EvalError into the pair.eval_error record
                        raise EvalError(code=EvalErrorCode.context_length_exceeded, inner_error=error)
                    case (together.error.InvalidRequestError, 400, "invalid_request_error") if error_obj["message"] == "Input validation error":
                        raise EvalError(code=EvalErrorCode.string_above_max_length, inner_error=error)
                    case (together.error.InvalidRequestError, 400, "invalid_request_error") if error_obj["message"].startswith("This model\'s maximum context length is "):
                        raise EvalError(code=EvalErrorCode.context_length_exceeded, inner_error=error)
                    case (together.error.InvalidRequestError, 400, "invalid_request_error") if error_obj["message"] == "All connection attempts failed":
                        # sleep and cotinue errors
                        await asyncio.sleep(60)
                        continue
                    case (together.error.InvalidRequestError, 400, "invalid_request_error") if error_obj["message"] == "Input validation error":
                        # sleep and cotinue errors
                        raise EvalError(code=EvalErrorCode.context_length_exceeded, inner_error=error)
                    case _:
                        raise error
            except together.error.Timeout as error:
                await asyncio.sleep(1)
                continue
            # except together.error.APIConnectionError as error:
                # raise error
            # directly raise
            # except together.error.AuthenticationError as error:
                # raise error
            
            # except Exception as error:
                # raise error
    return wrapper
