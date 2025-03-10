from enum import Enum

class DCEName(Enum):
    PROBLEM_P_C   = "p.c"
    PROBLEM_P1_C  = "p1.c"
    PROBLEM_P2_C  = "p2.c"
    TARGET_C      = "target.c"
    EQ_C          = "eq.c"
    NEQ_C         = "neq.c"  
    #C             = "c"

class TVEName(Enum):
    TEMPLATE      = "{index}.cu"
    WILDCARD      = "*.cu"

class OJName(Enum):
    ACCEPTED       = "accepted"
    WRONG          = "wrong"
    OBFUS_ACCEPTED = "obfus_accepted"
    OBFUS_WRONG    = "obfus_wrong"
    TEMPLATE       = "{label}_{index}.py"
    HTML_TEMPLATE  = "{name}.html"
    PROBLEM_HTML   = "problem.html"
    WILDCARD       = "*.py"
    # PY             = "py"

    @classmethod
    def all_labels(cls):
        return [cls.ACCEPTED, cls.WRONG, cls.OBFUS_ACCEPTED, cls.OBFUS_WRONG]

class STOKEName(Enum):
    INFO_JSON       = "info.json"
    TARGET_S        = "target.s"
    TESTCASES_TC    = "testcases.tc"
    SYNTHESIZE_CONF = "synthesize.conf"
    SYNTHESIZE_LOG  = "synthesize.log"
    RESULT_S        = "result.s"

    ALL             = "all"
    EQ              = "eq"
    NEQ             = "neq"
    TEMPLATE        = "{label}_{index}.s"
    WILDCARD        = "*.s"

class OriginalDataDirName(Enum):
    Data           = "data"
    RESULT_STEP_2  = "result_step2"

class MossFileName(Enum):
    MOSS           = "moss"
    MOSS_JSON      = "moss.json"

class organizeFileName(Enum):
    MAP_JSON = "organize_map.json"

class DataFileName(Enum):
    PAIRS_JSON     = "pairs.json"

class EvalFileName(Enum):
    EVAL_MODEL_TEMPLATE = "{prompt_type_name}/{model_family}/{model}"
    PAIR_CSV            = "eval_pairs.csv"
    PAIR_JSON           = "eval_pairs.json"

class FileName(Enum):
    HTML                          = "html"
    STAT_FIG_LENGTH_PNG            = "stat_fig_length_{label}.png"
    STAT_FIG_SIMILARITY_PNG        = "stat_fig_similarity_{label}.png"
    STAT_CORRELATION_TXT_FILE_NAME = "stat_correlation.txt"

class InfoDictKey(Enum):
    DEF_IN         = "def_in"
    LIVE_OUT       = "live_out"
    DEF_IN_COUNT   = "def_in_count"
    LIVE_OUT_COUNT = "live_out_count"
    TARGET         = "target"
    HEAD_COMMENT   = "head_comment"

__all__ = ["DCEName", "TVEName", "OJName", "STOKEName", "OriginalDataDirName", "MossFileName", "organizeFileName", "DataFileName", "EvalFileName", "FileName", "InfoDictKey"]  # Limits what gets exported with `from util import *