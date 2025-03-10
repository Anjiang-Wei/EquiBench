import asyncio
from functools import partial, wraps
from pathlib import Path
import shutil
import logging

import dotenv

def prepare_environment(log_level: int):
    # Load enviroment variables for API keys
    dotenv.load_dotenv()

    # Setup logging
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def parse_log_level(log_level_name: str) -> int:
    return int(getattr(logging, log_level_name.upper(), logging.INFO))

def excludeIfNone(value):
    """Do not include field for None values"""
    return value is None

def similarity_pair(similarities_dict: dict[tuple[Path, Path], tuple[float, float]], program_1_path: Path, program_2_path: Path) -> tuple[float, float]:
    return similarities_dict.get((program_1_path, program_2_path)) or reverse(similarities_dict.get((program_2_path, program_1_path))) or (0.0, 0.0)

def reverse(pair: tuple[float, float] | None) -> tuple[float, float] | None:
    return pair and pair[::-1]

def rm_mkdir(dst: Path):
    shutil.rmtree(path=dst, ignore_errors=True)
    dst.mkdir(parents=True, exist_ok=True)

def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run

"""
def retry_openai(func):
    @wraps(func)
    async def run(*args, **kwargs):
        while True:
            try:
                return await func(*args, **kwargs)
            except (RateLimitError, InternalServerError) as error:
                logging.error(f"[retry_openai]{error}")
                if error.code == "insufficient_quota":
                    raise error
                if error.code == "rate_limit_exceeded":
                    await asyncio.sleep(1)
                    continue
                else:
                    await asyncio.sleep(1)
                    continue   
            except APIConnectionError as error: 
                logging.error(f"[retry_openai]{error}")
                await asyncio.sleep(1)
                continue         
            except Exception as error:
                logging.error(error)
                raise error
    return run
"""
""""
    client = aisuite.Client()
    with ProcessPoolExecutor() as executor:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            executor=executor, 
            func=partial(
                client.chat.completions.create,
                messages=messages,
                model   =f"{model_platform}:{model_name}" 
            )
        )
"""