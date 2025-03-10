from enum import Enum
import random
from typing import Optional

from type import Pair, PromptType, Prompt

class EvalErrorCode(Enum):
    string_above_max_length = "string_above_max_length"
    context_length_exceeded = "context_length_exceeded"
    output_parse_error      = "output_parse_error"
    other_error             = "other_error"

class EvalError(Exception):
    """Custom error type for evaluation."""
    def __init__(self, code: EvalErrorCode, content: Optional[str] = None, inner_error: Optional[Exception] = None):
        if inner_error is not None:
            super().__init__(code, content, *inner_error.args)
        else:
            super().__init__(code, content)
        
        self.code        = code
        self.content     = content
        self.inner_error = inner_error

    def __repr__(self):
        return \
f"""EvalError(
    code        = {self.code}
    content     = {self.content}
    inner_error = (
        type={type(self.inner_error)}
        __str__={self.inner_error}
        args=(
        {"            \n".join(self.args)}
    )
)"""
    
class EvalInput:
    def __init__(self, pair: Pair, prompt_type: PromptType, model_with_platform: str, prompt: Prompt):       
        self.pair                 = pair 
        self.prompt_type          = prompt_type
        self.model_with_platform  = model_with_platform
        self.prompt               = prompt

    @property
    def model_names(self):
        model_names = self.model_with_platform.split("/")
        assert len(model_names) == 2
        return model_names

    @property 
    def model_platform(self):
        return self.model_names[0]

    @property 
    def model_name(self):
        return self.model_names[1]

    @property
    def prompt_str(self):
        return self.prompt.format(pair=self.pair)
    
    @property
    def messages(self):
        return [{"role": "user", "content": self.prompt_str}]
    
    def __repr__(self):
        return \
f"""EvalInput(
    prompt_type    = {self.prompt_type}
    mode           = {self.model_with_platform}
    category       = {self.pair.category}
    pair_id        = {self.pair.pair_id}
    truth_label    = {self.pair.truth_label} 
    program_1_path = {self.pair.program_1_path} 
    program_2_path = {self.pair.program_2_path}
)"""
    
class EvalOutput:
    def __init__(self, pred_original: Optional[bool], content: Optional[str], eval_error: Optional[EvalError]):
        self.pred_original    = pred_original
        self.pred_final       = pred_original if pred_original is not None else random.choice([True, False])
        self.content          = content
        self.eval_error       = eval_error
    
    def __repr__(self):
        return \
f"""EvalOutput(
    content        = {self.content}
    pred_original  = {self.pred_original}
    pred_final     = {self.pred_final}
    eval_error     = {self.eval_error}
)"""
        
    def accuracy(self, truth_label: bool) -> float:
        return 1.0 if self.pred_final == truth_label else 0.0
