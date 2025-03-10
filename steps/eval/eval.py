import logging
from typing import Optional

from llm import llm_generate, llm_judge
from type import Category, Pair, Prompt, PromptType
from .type import EvalInput, EvalOutput, EvalError, EvalErrorCode

async def pair_evalute(pair: Pair, prompt_type: PromptType, model: str, category: Category, prompt: Prompt):
    input = EvalInput(pair=pair, prompt_type=prompt_type, model_with_platform=model, prompt=prompt)
    logging.info (f"[Eval Start] - {input} - {prompt}")
    output = await evaluate(input=input)
    logging.info (f"[Eval End] - {output}")

    eval_error_message = f"{output.eval_error}" if output.eval_error is not None else None
    eval_error_code    = output.eval_error.code.value if output.eval_error is not None else None
    stat_accuracy      = output.accuracy(truth_label=pair.truth_label)

    return Pair(
        pair_id               = pair.pair_id,
        eval_prompt_type      = prompt_type,
        eval_model            = model,
        category              = category,

        truth_label           = pair.truth_label,

        # eval_pred_label       = output.pred_label, # deprecated
        eval_content          = output.content,
        stat_accuracy         = stat_accuracy,

        eval_error_message    = eval_error_message,
        eval_error_code       = eval_error_code,

        eval_pred_fixed       = output.pred_fixed,
        eval_pred_fixed_label = output.pred_fixed_label
    )

async def evaluate(input: EvalInput) -> EvalOutput:
    try:
        content = await llm_generate(input=input)
        return await eval_output_from_llm_generated(input=input, content=content)
    
    # write EvalError into the pair.eval_error record
    except EvalError as eval_error:
        return eval_output_from_eval_error(eval_error=eval_error)

"""
async def pairs_evaluate(pairs: list[Pair], prompt_type: PromptType,  model: str, category: Category, prompt: Prompt):
    return [await pair_evalute(pair=pair, prompt_type=prompt_type, model=model, category=category, prompt=prompt) for pair in pairs]
    # pair_tasks = [pair_evalute(pair=pair, prompt_type=prompt_type, model=model, category=category, prompt=prompt) for pair in pairs]
    # return await asyncio.gather(*pair_tasks)
"""
"""
async def pairs_evaluate_openai_batch(pairs: list[Pair], prompt_type: PromptType, model: str, category: Category, prompt: Prompt):
    # Open the file in write mode
    model_name  = model.split("/")[1]
    file_name = f"data_{prompt_type.value}_{model.replace(old="/", new="_")}.jsonl"
    with open(file_name, 'w') as file:
        for pair in pairs:
            prompt_str = prompt.format(pair=pair)
            messages  = [{"role": "user", "content": prompt_str}]
            entry = {"custom_id": pair.pair_id, "method": "POST", "url": "/v1/chat/completions", "body": {"model": model_name, "messages": messages}}

            # Write each dictionary as a JSON object on a new line
            file.write(json.dumps(entry) + '\n')
    
    client = OpenAI()
    batch_input_file = client.files.create(
        file=open(file_name, "rb"),
        purpose="batch"
    )
    batch_input_file_id = batch_input_file.id
    client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": "nightly eval job"
        }
    )
"""

def eval_output_from_eval_error(eval_error: EvalError, content: Optional[str] = None):
    return EvalOutput(
        pred_fixed = None,
        content    = content or eval_error.content,
        eval_error = eval_error
    )

async def eval_output_from_llm_generated(input: EvalInput, content: str):
    if content.strip() in ["YES", "YES\n```"]:
        pred_fixed = True
        
    elif content.strip() in  ["NO", "No\n```"]:
        pred_fixed = False
    
    else:
        pred_fixed = await llm_judge(content=content)
        logging.info(
f"""
[LLM Judge Generated]
====================[input     ]====================
 {input}
====================[content   ]====================
{content}
====================[pred_fixed]====================
{pred_fixed}
"""
        )

    if pred_fixed is None:
        raise EvalError(code=EvalErrorCode.output_parse_error, content = content, inner_error=None)
    
    return EvalOutput(
        pred_fixed = pred_fixed, 
        content    = content,
        eval_error = None
    )
