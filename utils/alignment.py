import re
from typing import Dict, List, Set

# Keep this stopword list simple + stable
STOPWORDS = set("""
a an the and or but if then else for to of in on with by from as at is are was were be been being
this that these those it its i you we they he she them our your my
""".split())

def normalize_tokens(text: str) -> List[str]:
    """
    Day 4 core: UNIGRAMS ONLY (no bigrams).
    Goal: stable, explainable, no fake phrases like 'adl glue'.
    """
    if not text:
        return []

    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = [t for t in text.split() if t not in STOPWORDS and len(t) > 2]
    return tokens

def alignment_facts(resume_text: str, jd_text: str, top_n: int = 25) -> Dict[str, object]:
    """
    Directional JD alignment facts:
    - score is % of JD terms covered by resume terms
    - returns facts (for comparison before vs after)
    """
    resume_terms: Set[str] = set(normalize_tokens(resume_text))
    jd_terms: Set[str] = set(normalize_tokens(jd_text))

    matched = sorted(resume_terms.intersection(jd_terms))
    missing = sorted(jd_terms.difference(resume_terms))

    score = 0
    if jd_terms:
        score = round((len(matched) / len(jd_terms)) * 100)

    return {
        "score": score,
        "jd_terms_count": len(jd_terms),
        "resume_terms_count": len(resume_terms),
        "matched_count": len(matched),
        # Keep these for backend/debug only (UI can choose to hide)
        "matched_preview": matched[:top_n],
        "missing_preview": missing[:top_n],
    }