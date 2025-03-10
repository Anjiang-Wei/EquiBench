import asyncio
from typing    import Optional
from anthropic import APIConnectionError, InternalServerError, RateLimitError
from openai    import AsyncOpenAI
from pydantic  import BaseModel

class CodeEquivalentResult(BaseModel):
    equivalent: Optional[bool]
    
async def judge_openai(content: str):
    client = AsyncOpenAI()
    while True:
        try:
            completion = await client.beta.chat.completions.parse(
            model="gpt-4o-2024-11-20",
            messages=[
                {"role": "system", "content": "Extract the code equivalent answer from text, the text answer YES means equivalent, answer NO means inequivalent. True for equivalent, False for not quivalent. If it is not decidable, return None. "},
                {"role": "user", "content": content},
            ],
                response_format=CodeEquivalentResult,    
            )
            result = completion.choices[0].message.parsed
            return result.equivalent
        except (RateLimitError, InternalServerError, APIConnectionError) as error:
            match error.code:
                case "rate_limit_exceeded":
                    # Error code: 429 - {'error': {'message': 'Rate limit reached for gpt-4o in organization org-tHX7813yeiJY2uTj13V8QSmP on tokens per min (TPM): Limit 30000, Used 29929, Requested 72. Please try again in 2ms. Visit https://platform.openai.com/account/rate-limits to learn more.', 'type': 'tokens', 'param': None, 'code': 'rate_limit_exceeded'}}
                    if error.message.find("tokens per min (TPM)") != -1:
                        await asyncio.sleep(60)
                    else:
                        await asyncio.sleep(1)
                    continue
                case "insufficient_quota":
                    raise error
                case _:
                    raise error

async def llm_judge(content: str):
    content = content.strip()
    sentences = [sentence.strip() for sentence in content.rstrip(".").split(".")]

    if not sentences:
        return None
    
    # Check the last two sentence
    last_sentence = sentences[-1]
    result = await judge_openai(content=last_sentence)
    if result is not None:
        return result
    
    if len(sentences) >= 2:
        last_two_sentence = sentences[-2:]
        result = await judge_openai(content=".".join(last_two_sentence))
        if result is not None:
            return result
    
    result = await judge_openai(content=content)
    return result
