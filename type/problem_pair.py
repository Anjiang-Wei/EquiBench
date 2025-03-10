from dataclasses import dataclass, field, replace
import json
import jsonlines
import logging
from pathlib import Path
from typing import Optional, Self

from dataclasses_json import config, dataclass_json
import pandas as pd

from utils        import excludeIfNone
from .category    import Category
from .prompt_type import PromptType

@dataclass_json
@dataclass
class Problem:
    category    : Category
    problem_id  : int
    
    path        : Path

    pairs       : list['Pair']
    
    def_in      : Optional[str]   = field(default=None, metadata=config(exclude=excludeIfNone))
    live_out    : Optional[str]   = field(default=None, metadata=config(exclude=excludeIfNone))
    html_path   : Optional[Path]  = field(default=None, metadata=config(exclude=excludeIfNone))
    html_content: Optional[str]   = field(default=None, metadata=config(exclude=excludeIfNone))
    @property
    def pair_id_only(self):
        return Problem(
            category   = self.category,
            problem_id = self.problem_id,
            path       = self.path,
            pairs      = [pair.pair_id_only for pair in self.pairs],
            def_in     = self.def_in,
            live_out   = self.live_out
        )

    @property
    def program_paths(self):
        return set([path for pair in self.pairs for path in pair.program_paths])
    
    @classmethod
    def save(cls, category: Category, problems: list[Self], path: Path, keep_pair_id_only: bool = True, jsonl: bool = False):
       
        path.parent.mkdir(parents=True, exist_ok=True)
        objs = [problem.pair_id_only.to_dict() if keep_pair_id_only else problem.to_dict()  for problem in problems]
        
        with open(path, "w") as file:
            json.dump(objs, file, indent=4)
                
        if jsonl:
            with jsonlines.open(path.__fspath__() + "l", "w") as file:
                file.write_all(objs)
                
        logging.info(f"[Category: {category.value: <6}][Problem] Save {len(problems)} problems to \"{path}\"")

    @classmethod
    def load(cls, category: Category, json_path: Path):
        
        with open(json_path, "r") as file:
            objs = json.load(file)
            problems: list[Problem] = [Problem.from_dict(obj) for obj in objs]
        
        logging.info(f"[Category: {category.value: <6}][Problem] Load {len(problems)} problems from \"{json_path}\"")
        return problems 
    """
    @classmethod
    def load_by_group(cls, category: Category, path: Path, batch_size: int):
        problems       = cls.load(path)
        problem_groups = [problems[i:i + batch_size] for i in range(0, len(problems), batch_size)]
        logging.info(f"[Category: {category.value: <6}][Problem] Divide into {len(problem_groups)} problem groups (batch_size={batch_size})")
        return problem_groups
    """

    def with_content(self):
        if not self.html_path:
            return self
        with open(self.html_path, "r") as file:
            html_content = file.read()

        return replace(
            self,
            html_content=html_content
        )


@dataclass_json
@dataclass
class Pair:
    category            : Category
    pair_id             : int

    program_1_path      : Optional[Path      ] = field(default=None, metadata=config(exclude=excludeIfNone))
    program_2_path      : Optional[Path      ] = field(default=None, metadata=config(exclude=excludeIfNone))
    program_1_code      : Optional[str       ] = field(default=None, metadata=config(exclude=excludeIfNone))
    program_2_code      : Optional[str       ] = field(default=None, metadata=config(exclude=excludeIfNone))
    truth_label         : Optional[bool      ] = field(default=None, metadata=config(exclude=excludeIfNone))

    problem_id          : Optional[int       ] = field(default=None, metadata=config(exclude=excludeIfNone))
    problem_path        : Optional[Path      ] = field(default=None, metadata=config(exclude=excludeIfNone))
    problem_def_in      : Optional[str       ] = field(default=None, metadata=config(exclude=excludeIfNone))
    problem_live_out    : Optional[str       ] = field(default=None, metadata=config(exclude=excludeIfNone))
    problem_html_path   : Optional[Path      ] = field(default=None, metadata=config(exclude=excludeIfNone))
    problem_html_content: Optional[str       ] = field(default=None, metadata=config(exclude=excludeIfNone))

    program_1_length    : Optional[int       ] = field(default=None, metadata=config(exclude=excludeIfNone))
    program_2_length    : Optional[int       ] = field(default=None, metadata=config(exclude=excludeIfNone))
    program_1_similarity: Optional[float     ] = field(default=None, metadata=config(exclude=excludeIfNone))
    program_2_similarity: Optional[float     ] = field(default=None, metadata=config(exclude=excludeIfNone))

    eval_prompt_type    : Optional[PromptType] = field(default=None, metadata=config(exclude=excludeIfNone))
    eval_model          : Optional[str       ] = field(default=None, metadata=config(exclude=excludeIfNone))
    

    eval_content        : Optional[str       ] = field(default=None, metadata=config(exclude=excludeIfNone))
    
    stat_accuracy       : Optional[float     ] = field(default=None, metadata=config(exclude=excludeIfNone))
    eval_error_code     : Optional[str       ] = field(default=None, metadata=config(exclude=excludeIfNone))
    eval_error_message  : Optional[str       ] = field(default=None, metadata=config(exclude=excludeIfNone))
    
    eval_pred_original  : Optional[bool      ] = field(default=None, metadata=config(exclude=excludeIfNone)) # true, false, None
    eval_pred_final     : Optional[bool      ] = field(default=None, metadata=config(exclude=excludeIfNone)) # true, false, random([true, false])

    similarity           : Optional[float]     = field(default=None, metadata=config(exclude=excludeIfNone))
    length               : Optional[float]     = field(default=None, metadata=config(exclude=excludeIfNone))

    @property
    def pair_id_only(self):
        return Pair(category=self.category, pair_id=self.pair_id)
    
    @property
    def program_paths(self):
        return set([self.program_1_path, self.program_2_path])
    
    @property
    def is_same(self):
        with open(self.program_1_path, "r") as file:
            code1 = file.read()
        
        with open(self.program_2_path, "r") as file:
            code2 = file.read()

        code1 = "\n".join(line.strip() for line in code1.splitlines())
        code2 = "\n".join(line.strip() for line in code2.splitlines())

        return code1 == code2
    
    def with_length(self):
        with open(self.program_1_path, "r") as file:
            program_1_code = file.read()
        with open(self.program_2_path, "r") as file:
            program_2_code = file.read()

        program_1_length = program_1_code.strip().count("\n") + 1
        program_2_length = program_2_code.strip().count("\n") + 1

        return replace(
            self,
            program_1_length=program_1_length,
            program_2_length=program_2_length,
        )
    
    def with_content(self):
        with open(self.program_1_path, "r") as file:
            program_1_code = file.read()
        with open(self.program_2_path, "r") as file:
            program_2_code = file.read()
        
        problem_html_content = None
        if self.problem_html_path:
            with open(self.problem_html_path, "r") as file:
                problem_html_content = file.read()

        return replace(
            self,
            program_1_code=program_1_code,
            program_2_code=program_2_code,
            problem_html_content=problem_html_content
        )
    
    def with_pair_id(self, pair_id: int):
        return replace(self, pair_id=pair_id)

    @classmethod
    def save(cls, pairs: list[Self], category: Optional[Category], json_path: Path, csv_path: Path, additional: bool = False, jsonl: bool = False):        
        # json
        if additional:
            
            previous_pairs = cls.load(category=None, json_path=json_path) if json_path.exists() else list[Pair]()
            pairs = previous_pairs + pairs
        
        json_path.parent.mkdir(parents=True, exist_ok=True)

        objs = [pair.to_dict() for pair in pairs]
        with open(json_path, "w") as file:
            json.dump(objs, file, indent=4)
        
        if jsonl:
            with jsonlines.open(json_path.__fspath__() + "l", "w") as file:
                file.write_all(objs)
        
        # csv
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(objs).set_index("pair_id")
        df.to_csv(csv_path)
        category_label = category.value if category is not None else "ALL"

        # logging
        logging.info(f"[Category: {category_label: <6}][Pair   ] Save {len(pairs)} pairs to \"{json_path}\" and \"{csv_path}\"")
    
    @classmethod
    def load(cls, category: Optional[Category], json_path: Path):
        if not json_path.exists():
            return list[Pair]()

        with open(json_path, "r") as file:
            objs = json.load(file)
            pairs: list[Pair] = [Pair.from_dict(obj) for obj in objs]
        
        cls._log_pairs(category=category, verb="Load", pairs=pairs, path=json_path)
        return pairs 

    @classmethod
    def from_problems(cls, category: Optional[Category], problems: list[Problem], with_content: bool = False):        
        pairs = [pair.with_length() for problem in problems for pair in problem.pairs]
        if with_content:
            pairs = [pair.with_content() for pair in pairs]
        # pairs = [pair.with_pair_id(pair_id=index) for index, pair in enumerate(pairs)]
        cls._log_pairs(category=category, verb="Load (from problems)", pairs=pairs)
        return pairs

    @classmethod
    def _log_pairs(cls, category: Optional[Category], verb: str, pairs: list[Self], path: Path | None = None):
        all_pairs_count = len(pairs)
        eq_pairs_count  = len([pair for pair in pairs if pair.truth_label])
        neq_pairs_count = len([pair for pair in pairs if not pair.truth_label])
        
        category_label = category.value if category is not None else "ALL"
        from_path_label = f" from \"{path}\"" if path is not None else ""
        logging.info(f"[Category: {category_label: <6}][Pair   ] {verb} {all_pairs_count} pairs (eq = {eq_pairs_count} pairs, neq = {neq_pairs_count} pairs){from_path_label}")
