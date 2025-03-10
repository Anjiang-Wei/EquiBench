import json
import logging
from pathlib import Path
import re
from typing import Self
from dataclasses import dataclass
from urllib.request import urlopen

from bs4 import BeautifulSoup, ResultSet, Tag
from dataclasses_json import dataclass_json
import mosspy

from type import Category, FileName, Problem

@dataclass_json
@dataclass
class MossReportRow:
    url                 : str
    program_1_path      : Path
    program_2_path      : Path
    program_1_similarity: float
    program_2_similarity: float

    @classmethod
    def from_tuple(cls, row: tuple[Path, Path, float, float, str]) -> Self:
        return cls(
            url                  = row[4],
            program_1_path       = Path(row[0]),
            program_2_path       = Path(row[1]),
            program_1_similarity = row[2],
            program_2_similarity = row[3]
        )
    
    @classmethod
    def save(cls, category: Category, rows: list[Self], path: Path):
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as file:
            objs = [row.to_dict() for row in rows]
            json.dump(objs, file, indent=4)

        logging.info(f"[Category: {category.value: <6}][MossReportRow] Save {len(rows)} rows to \"{path}\"")

    @classmethod
    def load(cls, category: Category, path: Path):
        
        with open(path, "r") as file:
            objs = json.load(file)
            rows = [MossReportRow.from_dict(obj) for obj in objs]
        
        logging.info(f"[Category: {category.value: <6}][MossReportRow] Load {len(rows)} rows from \"{path}\"")
        return rows

class MossRequest:
    def __init__(self, moss_language: str, input_program_paths: set[Path], moss_path: Path, name: str, download_report: bool, log_level: int):
        self.moss_language   = moss_language
        self.name            = name
        self.download_report = download_report
        self.log_level       = log_level
        self.define_paths(input_program_paths=input_program_paths, moss_path=moss_path)

    def define_paths(self, input_program_paths: set[Path], moss_path: Path):
        # input paths
        self.input_program_paths = input_program_paths
        
        # output paths
        self.output_index_html_path = moss_path / f"{self.name}.{FileName.HTML.value}"
        self.output_report_path     = moss_path / self.name

    def send(self, index: int) -> str:
        client = self._client(index=index)
        
        # send
        url = client.send()  
        logging.info(f"[MossRequest] Moss.send()=\"{url}\"")
        


        # download report
        if self.download_report:
            # save
            """
            self.output_index_html_path.parent.mkdir(parents=True, exist_ok=True)
            client.saveWebPage(url=url, path=self.output_index_html_path.__fspath__())
            logging.info(f"[MossRequest] Moss.save_web_page(path=\"{self.output_index_html_path}\")")
            """
            self.output_report_path.parent.mkdir(parents=True, exist_ok=True)
            mosspy.download_report(url=url, path=self.output_report_path.__fspath__(), connections=8, log_level=self.log_level, on_read=lambda _: print("*", flush=True))
            logging.info(f"[MossRequest] Moss.download_report(path=\"{self.output_report_path}\")")
        
        return url
    
    def _client(self, index: int):
        moss_user_ids = [880435682, 780239634, 115327304, 14851489, 784508079]
        moss_user_id  = moss_user_ids[index % len(moss_user_ids)]
        moss_language = self.moss_language
        client = mosspy.Moss(user_id=moss_user_id, language=moss_language)
        logging.info(f"[MossRequest] Moss._client(index={index}, name={self.name})")
        logging.info(f"[MossRequest] Moss.__init__(userid={moss_user_id}, language={moss_language}")

        for path in self.input_program_paths:
            try:
                client.addFile(path.__fspath__())
                logging.info(f"[MossRequest] Moss.addFile(\"{path}\")")
            except Exception as e: # empty file
                logging.info(f"[MossRequest] Moss.addFile(\"{path}\") error: {e}")
        
        return client

    @classmethod
    def from_problems(cls, moss_language: str, problems: list[Problem], moss_path: Path, download_report: bool, log_level: int) -> Self:
        if len(problems) == 1:
            name = f"problem{problems[0].problem_id}"
        else:
            name = f"problem{problems[0].problem_id}-problem{problems[-1].problem_id}"
            
        program_paths = set([path for problem in problems for path in problem.program_paths])
        
        return MossRequest(
            moss_language      =moss_language,
            input_program_paths=program_paths, 
            moss_path          =moss_path, 
            name               =name, 
            download_report    =download_report,
            log_level          =log_level
        )
    
class MossHTML:
    def __init__(self, url: str):
        self.url     = url

        # open url
        response = urlopen(url)
        charset = response.headers.get_content_charset()
        self.content = response.read().decode(charset)

    def rows(self):
        soup = BeautifulSoup(self.content, "html.parser")
        table = soup.find("table")
        if not table:
            logging.error(f"[MossIndexHTML] No table found in Moss results at \"{self.url}\"")
            return list[MossReportRow]() # return empty list
        
        rows = self._read_rows_from_table(table)
        logging.info(f"[MossIndexHTML] Read {len(rows)} rows from \"{self.url}\"")
        return rows
        
    def _read_rows_from_table(self, table: Tag) -> list[MossReportRow]:
        input_rows = table.find_all("tr")[1:] # Skip header row
        ourput_rows = [self._read_row(row) for row in input_rows]

        # Compact the results by removing None values
        return [output_row for output_row in ourput_rows if output_row is not None]

    def _read_row(self, row: Tag) -> MossReportRow | None:
        cols: ResultSet[Tag] = row.find_all("td")
        
        if len(cols) < 2:
            return None
            
        file1_text = cols[0].get_text(strip=True)
        file2_text = cols[1].get_text(strip=True)

        # Use regex to find the numeric percentage inside parentheses
        m1 = re.search(r"\((\d+)%\)", file1_text)
        m2 = re.search(r"\((\d+)%\)", file2_text)
        if not m1 or not m2:
            # If we can't find percentages, skip this row
            return None

        program_1_similarity = float(m1.group(1)) / 100.0
        program_2_similarity = float(m2.group(1)) / 100.0

        # Extract file paths (everything before " (")
        program_1_path = Path(file1_text.split(" (")[0].strip())
        program_2_path = Path(file2_text.split(" (")[0].strip())

        return MossReportRow(
            url=self.url, 
            program_1_path=program_1_path, 
            program_2_path=program_2_path, 
            program_1_similarity=program_1_similarity, 
            program_2_similarity=program_2_similarity
        )