from dataclasses import dataclass
import logging
from pathlib import Path
import yaml

from .problem_pair        import Pair
from .category    import Category
from .prompt_type import PromptType
"""
NO = "no"
YES = "yes"
NOT = "not"
EQUIVALENT = "equivalent"
INEQUIVALENT = "inequivalent"
"""

@dataclass
class Prompt:
    prompt_type: PromptType
    prompt: str
    true_label: str
    false_label: str

    def __repr__(self):
        return \
f"""Prompt(
    prompt_type = {self.prompt_type}
    true_label  = {self.true_label}
    false_label = {self.false_label}
    prompt      = {self.prompt}
)"""    
    @classmethod
    def load(cls, category: Category, prompt_type: PromptType, prompts_yaml_path: Path):
        with open(file=prompts_yaml_path, mode="r") as file:
            data = yaml.safe_load(file)
            prompt = cls(
                prompt_type    = prompt_type,
                prompt         = data[category.value][prompt_type.value],
                true_label     = data["true_label"],
                false_label    = data["false_label"]
            )
        logging.info(f"[LOAD PROMPT][{category.value}][{prompt_type.value}]:\n{prompt}")
        return prompt

    def format(self, pair: Pair):
        program_1_code = pair.program_1_code
        if program_1_code is None:
            assert pair.program_1_path, "pair.program_1_path should exist"

            with open(file=pair.program_1_path, mode="r") as file:
                program_1_code = file.read()
        
        program_2_code = pair.program_2_code
        if program_2_code is None:
            assert pair.program_2_path, "pair.program_2_path should exist"
            with open(file=pair.program_2_path, mode="r") as file:
                program_2_code = file.read()

        match pair.category:
            case Category.STOKE:
                original_prompt_str = self.prompt.format(
                    true_label     = self.true_label, 
                    false_label    = self.false_label,
                    program_1_code = program_1_code, 
                    program_2_code = program_2_code,
                    def_in         = pair.problem_def_in,
                    live_out       = pair.problem_live_out 
                )
            case Category.OJ_V | Category.OJ_A | Category.OJ_VA:
                problem_html_content = pair.problem_html_content
                if problem_html_content is None:
                    assert pair.problem_html_path, "pair.problem_html_path should exist"
                    with open(file=pair.problem_html_path, mode="r") as file:
                        problem_html_content = file.read()

                original_prompt_str = self.prompt.format(
                    true_label     = self.true_label, 
                    false_label    = self.false_label,
                    program_1_code = program_1_code, 
                    program_2_code = program_2_code,
                    problem_html   = problem_html_content
                )
            case _:
                original_prompt_str = self.prompt.format(
                    true_label     = self.true_label, 
                    false_label    = self.false_label,
                    program_1_code = program_1_code, 
                    program_2_code = program_2_code
                )

        prompt_str = bytes(original_prompt_str, "utf-8").decode("utf-8", "replace")
        return prompt_str

    """
    # Function to judge based on sentence
    @classmethod
    def judge_sentences(cls, sentences: list[str]):
        if not sentences:
            return None
        
        # Check the last sentence
        last_sentence = sentences[-1]
        result = cls.judge_sentence(last_sentence)
        if result is not None:
            return result
        
        # Check the last two sentence
        if len(sentences) >= 2:
            last_two_sentence = sentences[-2]
            result = cls.judge_sentence(last_two_sentence)
            if result is not None:
                return result

        
        # Check the first sentence
        first_sentence = sentences[0]
        result = cls.judge_sentence(first_sentence)
        if result is not None:
            return result
        

        return None
    """
    
    # Function to judge based on sentence
    """
    @classmethod
    def judge_sentence(self, sentence: str):
        words = set(map(str.lower, re.findall(r"\w+|[^\w\s]", sentence)))
        
        if sentence == "Let’s analyze the problem and break it down step by step to decide whether the two programs are semantically equivalent":
            return None
        if sentence == "If you provide [Program 2], I can help evaluate whether the two programs are equivalent or not":
            return None
        if sentence == "(The programs cannot be judged as equivalent because Program 2 is missing":
            return None
        
        if NO in words or (NOT in words and EQUIVALENT in words) or INEQUIVALENT in words:
            return False
        if YES in words or EQUIVALENT in words:
            return True
        return None
    """
