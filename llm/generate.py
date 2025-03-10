# from litellm import completion
import anthropic
import together
import openai

from steps.eval.type import EvalInput
from .utils import log_error_wrapper,  handle_error_openai, handle_error_anthropic, handle_error_together

async def llm_generate(input: EvalInput) -> str:
    match input.model_platform:
        case "openai":
            return await generate_openai(input=input)
        case "anthropic":
            return await generate_anthropic(input=input)
        case _:
            return await generate_together(input=input)

@handle_error_openai
@log_error_wrapper
async def generate_openai(input: EvalInput) -> str:
    client = openai.AsyncClient()
    chat_completion = await client.chat.completions.create(
        messages = input.messages,
        model    = input.model_name,
        # timeout  = 60 * 5
    )
    return chat_completion.choices[0].message.content

@handle_error_anthropic
@log_error_wrapper
async def generate_anthropic(input: EvalInput) -> str:
    client = anthropic.AsyncClient()
    message = await client.messages.create(
        max_tokens = 8192,
        model      = input.model_name,
        messages   = input.messages
    )
    return "".join([block.text for block in message.content])

@handle_error_together
@log_error_wrapper
async def generate_together(input: EvalInput) -> str:
    client = together.AsyncClient()
    chat_completion = await client.chat.completions.create(
        messages=input.messages,
        model   =f"{input.model_platform}/{input.model_name}" 
    )
    return chat_completion.choices[0].message.content

"""
@handle_error_deepseek
@log_error_wrapper
async def generate_deepseek(input: EvalInput) -> str:
    deepseek_api_key = os.environ["DEEPSEEK_API_KEY"]
    deepseek_base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    client = openai.AsyncClient(api_key=deepseek_api_key, base_url=deepseek_base_url)
    chat_completion = await client.chat.completions.create(
        messages = input.messages,
        model    = input.model_name,
        # timeout  = 60 * 5
    )
    return chat_completion.choices[0].message.content

#@handle_aisuide_error
@log_error_wrapper
@async_wrap
def create_completion_aisuite(input: EvalInput) -> str:
    client = aisuite.Client()
    chat_completion = client.chat.completions.create(
        messages = input.messages,
        model    = f"{input.model_platform}:{input.model_name}" 
    )
    return chat_completion.choices[0].message.content
"""