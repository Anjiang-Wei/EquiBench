# Python >= 3.11

# python3 step3_eval.py data eval --prompt_types ZERO ZERO_COT --models gpt-4o-mini-2024-07-18 --categories DCE TVM --limit 5

import argparse
import asyncio
import logging
from pathlib import Path
from typing import Optional

from utils import prepare_environment, parse_log_level
from type  import Category, Pair, Prompt, PromptType, DataFileName, EvalFileName
from steps import pair_evalute 

def main():
    eval_step = EvalStep(**vars(parse_args()))
    asyncio.run(eval_step())

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate program equivalence using OpenAI GPT models.")
    parser.add_argument("data_path"      , type=Path           ,                                                                           help="The file path of datasets. (input)")
    parser.add_argument("eval_path"      , type=Path           ,                                                                           help="The folder path of eval. (output)")
    parser.add_argument("--prompt_types" , type=str            , required=False, default=["ZERO", "FEW", "ZERO_COT","FEW_COT"]           , help="prompt types.", choices=["ZERO", "FEW", "ZERO_COT", "FEW_COT"], nargs="+")
    parser.add_argument("--models"       , type=str            , required=False, default=["meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"] , help="models to use (e.g., gpt-4o, gpt-3.5-turbo).", nargs="+")
    parser.add_argument("--categories"   , type=str            , required=False, default=["DCE", "TVM", "STOKE", "OJ_V", "OJ_A", "OJ_VA"], help="Which category of the experiment.", choices=["DCE", "TVM", "STOKE", "OJ_V", "OJ_A", "OJ_VA"], nargs="+")
    parser.add_argument("--prompt_path"  , type=Path           , required=False, default=Path("prompts.yaml")                            , help="prompt path.")
    parser.add_argument("--limit"        , type=int            , required=False, default=None                                            , help="Optional limit as an integer.")
    parser.add_argument("--log_level"    , type=parse_log_level, required=False, default="INFO"                                          , help="Set logging level.", choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    return parser.parse_args()

class EvalStep:
    def __init__(self, prompt_types: list[str], models: list[str], categories: list[str], prompt_path: Path, data_path: Path, eval_path: Path, log_level: str, limit: Optional[int]):
        prepare_environment(log_level=log_level)   
        typed_categories = [Category.from_value(category_name=category) for category in categories]
        typed_prompt_types = [PromptType.from_value(prompt_type_value=pormpt_type) for pormpt_type in prompt_types]
        self.define_paths(eval_path=eval_path)     

        logging.info(f"EvalStep(prmpt_types={prompt_types}, models={models}, categories={categories}, limit={limit})")
        
        self.substeps = [
            EvalStepForCategoryModel(
                prompt_type     = prompt_type,
                model           = model,
                category        = category, 
                prompt_path     = prompt_path,
                data_path       = data_path / category.value, 
                eval_path       = eval_path / EvalFileName.EVAL_MODEL_TEMPLATE.value.format(prompt_type_name=prompt_type.value, model_family=model.split("/")[0], model=model.split("/")[1]) / category.value,
                summary_path    = eval_path,
                limit           = limit
            ) for model in models for prompt_type in typed_prompt_types for category in typed_categories
        ]
    
    def define_paths(self, eval_path: Path):
        # input paths
        
        # output paths
        self.eval_path       = eval_path
        self.summary_csv_path = eval_path / EvalFileName.PAIR_CSV.value
        self.summary_json_path = eval_path / EvalFileName.PAIR_JSON.value
    
    async def __call__(self):
        self.eval_path.mkdir(parents=True, exist_ok=True)

        # Run all steps concurrently
        step_tasks = [substep() for substep in self.substeps]
        pair_groups = await asyncio.gather(*step_tasks)
        pairs = [pair for pairs in pair_groups for pair in pairs]
        Pair.save(pairs=pairs, category=None, json_path=self.summary_json_path, csv_path=self.summary_csv_path, additional=True)

        #self.eval_path.mkdir(parents=True, exist_ok=True) # do not rm, just mkdir
        #await asyncio.gather(*[substep.run() for substep in self.substeps])

class EvalStepForCategoryModel:
    def __init__(self, prompt_type: PromptType, model: str, category: Category, prompt_path: Path, data_path: Path, eval_path: Path, summary_path: Path, limit: Optional[int]):        
        self.prompt_type = prompt_type
        self.model       = model
        self.category    = category
        self.limit       = limit

        self.define_paths(prompt_path=prompt_path, data_path=data_path, eval_path=eval_path, summary_path=summary_path)

    def define_paths(self, prompt_path: Path, data_path: Path, eval_path: Path, summary_path: Path):
        pass
        # input paths
        self.prompts_yaml_path = prompt_path
        self.data_path         = data_path
        self.pairs_json_path   = data_path / DataFileName.PAIRS_JSON.value

        # output paths
        self.eval_path      = eval_path
        self.eval_csv_path  = eval_path / EvalFileName.PAIR_CSV.value
        self.eval_json_path = eval_path / EvalFileName.PAIR_JSON.value
        self.summary_csv_path = summary_path / EvalFileName.PAIR_CSV.value
        self.summary_json_path = summary_path / EvalFileName.PAIR_JSON.value

    async def __call__(self):
        self.eval_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"EvalStepForCategoryModel(prmpt_type={self.prompt_type}, model={self.model}, category={self.category}, limit={self.limit})")
        
        # load
        pairs = Pair.load(category=self.category, json_path=self.pairs_json_path)
        evaled_pairs = Pair.load(category=self.category, json_path=self.eval_json_path)

        # filter by limit
        if self.limit is not None:
            pairs = pairs[:self.limit]
        

        # filter by evaluated pairs
        for eval_pair in evaled_pairs:
            assert eval_pair.category == self.category and eval_pair.eval_model == self.model and eval_pair.eval_prompt_type == self.prompt_type, "Pair not match"
        evaled_pair_ids = set([eval_pair.pair_id for eval_pair in evaled_pairs])
        
        pairs = [pair for pair in pairs if pair.pair_id not in evaled_pair_ids]

        # prompt
        prompt = Prompt.load(category=self.category, prompt_type=self.prompt_type, prompts_yaml_path=self.prompts_yaml_path)

        for pair in pairs:
            # eval
            evaled_pair = await pair_evalute(pair=pair, prompt_type=self.prompt_type, model=self.model, category=self.category, prompt=prompt)
            evaled_pairs.append(evaled_pair)
            
            # save
            Pair.save(pairs=evaled_pairs, category=self.category, json_path=self.eval_json_path, csv_path=self.eval_csv_path)

        return evaled_pairs

if __name__ == "__main__":
    main()
