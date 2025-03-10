   
from pathlib import Path
from typing import Optional
from dataclasses import replace

from sklearn.feature_extraction import text as sklearn_text

from type import Category, Pair
from utils import similarity_pair
from .type import MossReportRow

def pairs_with_similarity(category: Optional[Category], pairs: list[Pair], moss_json_path: Path): 
    match category:
        case Category.STOKE:
            pairs = [pair_with_jaccard(pair=pair) for pair in pairs]
        case _:
            moss_report_rows = MossReportRow.load(category=category, path=moss_json_path)
            similarities_dict = {(row.program_1_path, row.program_2_path): (row.program_1_similarity, row.program_2_similarity) for row in moss_report_rows}
    
            pairs = [pair_with_moss(pair=pair, similarities_dict=similarities_dict) for pair in pairs]
    
    Pair._log_pairs(category, verb="Update", pairs=pairs)
    return pairs

def pair_with_moss(pair: Pair, similarities_dict: dict[tuple[Path, Path], tuple[float, float]]):
    program_1_similarity, program_2_similarity = similarity_pair(similarities_dict, pair.program_1_path, pair.program_2_path)
    return replace(
        pair,
        program_1_similarity=program_1_similarity,
        program_2_similarity=program_2_similarity,
    )

def pair_with_jaccard(pair: Pair):
    program_1_similarity, program_2_similarity = jaccard_similarity(pair.program_1_path, pair.program_2_path)
    return replace(
        pair,
        program_1_similarity=program_1_similarity,
        program_2_similarity=program_2_similarity,
    )

def jaccard_similarity(program_1_path: Path, program_2_path: Path, n: int = 2) -> float:
    with open(file=program_1_path, mode="r") as file:
        program_1_code = file.read()

    with open(file=program_2_path, mode="r") as file:
        program_2_code = file.read()        

    # Ensure the inputs are not empty
    if not program_1_code.strip() or not program_2_code.strip():
        return 0.0

    # Preprocess the input (remove extra spaces and newlines)
    program_1_code = " ".join(line.strip() for line in program_1_code.strip().splitlines() if line.strip())
    program_2_code = " ".join(line.strip() for line in program_2_code.strip().splitlines() if line.strip())

    # Tokenize and create n-grams
    vectorizer = sklearn_text.CountVectorizer(analyzer="word", ngram_range=(n, n), stop_words=None)
    
    # Fit the vectorizer on combined input to ensure consistent vocabulary
    try:
        ngrams1 = set(vectorizer.fit_transform([program_1_code]).toarray().nonzero()[1])
        ngrams2 = set(vectorizer.fit_transform([program_2_code]).toarray().nonzero()[1])
    except ValueError:
        # Handle cases where tokenization fails (e.g., both inputs are empty)
        return 0.0
    
    # Compute Jaccard similarity
    intersection = len(ngrams1 & ngrams2)
    union = len(ngrams1 | ngrams2)
    similiarity = intersection / union if union != 0 else 0.0
    return similiarity, similiarity
