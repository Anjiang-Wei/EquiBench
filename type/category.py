from enum import Enum
from typing import Self

class Category(Enum):
    DCE   = "DCE"
    TVM   = "TVM"
    STOKE = "STOKE"
    OJ    = "OJ"
    OJ_V  = "OJ_V"
    OJ_A  = "OJ_A"
    OJ_VA = "OJ_VA"

    @classmethod
    def from_value(cls, category_name: str) -> Self:
        return getattr(cls, category_name.upper(), cls.DCE)
    
    def to_value(self) -> str:
        return self.value

    @classmethod
    def all_original_categories(cls):
        return [Category.DCE, Category.TVM, Category.STOKE, Category.OJ]
        
    @classmethod
    def all_eval_categories(cls):
        return [Category.DCE, Category.TVM, Category.STOKE, Category.OJ_V, Category.OJ_A, Category.OJ_VA]
    
    @property
    def organize(self) -> str:
        match self:
            case Category.DCE | Category.TVM | Category.STOKE:
                return self
            case Category.OJ | Category.OJ_V | Category.OJ_A | Category.OJ_VA:
                return Category.OJ
