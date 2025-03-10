from pathlib import Path
from typing import Optional

from dataclasses_json import cfg
from marshmallow import fields

from .category     import Category
from .problem_pair import Problem, Pair
from .prompt       import Prompt
from .prompt_type  import PromptType

__all__ = ["Category", "Pair", "Problem", "Prompt", "PromptType"]

from .names import *
from .names import __all__ as names_all
__all__ += names_all


# json_dataclasses

cfg.global_config.encoders [Path] = Path.__fspath__
cfg.global_config.decoders [Path] = Path
cfg.global_config.mm_fields[Path] = fields.String()

cfg.global_config.encoders [Optional[Path]] = lambda obj: None if obj is None else obj.__fspath__()
cfg.global_config.decoders [Optional[Path]] = lambda obj: None if obj is None else Path(obj)
cfg.global_config.mm_fields[Optional[Path]] = Optional[fields.String]

cfg.global_config.encoders [Optional[PromptType]] = lambda obj: None if obj is None else PromptType.to_value(obj)
cfg.global_config.decoders [Optional[PromptType]] = lambda obj: None if obj is None else PromptType.from_value(obj)
cfg.global_config.mm_fields[Optional[PromptType]] = Optional[fields.String]

cfg.global_config.encoders [Category] = Category.to_value
cfg.global_config.decoders [Category] = Category.from_value
cfg.global_config.mm_fields[Category] = fields.String()
