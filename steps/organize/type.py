from dataclasses import dataclass, field
import logging
from pathlib import Path

from type                  import Category, Problem
from steps.similarity.type import MossReportRow

@dataclass
class PathMap:
    to   : dict[Path: Path] = field(default_factory=dict)
    from_: dict[Path: Path] = field(default_factory=dict)

    @property
    def __dict__(self):
        return {
            "to"  : {str(k): str(v) for k, v in self.to   .items()},
            "from": {str(k): str(v) for k, v in self.from_.items()},
        }

    @classmethod
    def from_dict(cls, obj: dict[str, str]):
        return Problem(
            src_to_dst={Path(k) : Path(v) for k, v in obj["to"  ].items()},
            dst_to_src={Path(k) : Path(v) for k, v in obj["from"].items()}
        )
    
    def map_moss_report_row(self, category: Category, row: MossReportRow):
        if row.program_1_path not in self.to:
            logging.info(f"[Category: {category.value: <6}][PathMap] Ignore program path {row.program_1_path}")
            return None
        if row.program_2_path not in self.to:
            logging.info(f"[Category: {category.value: <6}][PathMap] Ignore program path {row.program_2_path}")
            return None
        return MossReportRow(
            url=row.url,
            program_1_path=self.to[row.program_1_path],
            program_2_path=self.to[row.program_2_path],
            program_1_similarity=row.program_1_similarity,
            program_2_similarity=row.program_2_similarity
        )
    