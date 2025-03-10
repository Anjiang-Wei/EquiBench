
from enum import Enum
from typing import Self

class PromptType(Enum):
    ZERO     = "ZERO"
    FEW      = "FEW"
    ZERO_COT = "ZERO_COT"
    FEW_COT  = "FEW_COT"

    @classmethod
    def from_value(cls, prompt_type_value: str) -> Self:
        return getattr(cls, prompt_type_value.upper(), cls.ZERO)
    
    @classmethod
    def to_value(cls, prompt_type: Self) -> str:
        return prompt_type.value

    @classmethod
    def all_prompt_types(cls):
        return [PromptType.ZERO, PromptType.FEW, PromptType.ZERO_COT, PromptType.FEW_COT]
