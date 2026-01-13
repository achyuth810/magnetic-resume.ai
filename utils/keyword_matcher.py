import re
from typing import List, Set, Dict

# Expanded stopwords list for better noise reduction
STOPWORDS = set("""
a about above after again against all am an and any are as at be because been before being below between both but by
can could did do does doing down during each few for from further had has have having he her here hers herself him himself
his how i if in into is it its itself just me more most my myself no nor not now of off on once only or other our ours
ourselves out over own same she should so some such than that the their theirs them themselves then there these they this
those through to too under until up very was we were what when where which while who whom why will with would you your yours
yourself yourselves
""".split())

def simple_stem(word: str) -> str:
    """
    Basic manual stemmer to handle common suffixes (inspired by Porter stemmer).
    This reduces variations like 'developing' -> 'develop', 'developed' -> 'develop'.
    """
    if word.endswith('ing'):
        word = word[:-3]
    elif word.endswith('ed'):
        word = word[:-2]
    elif word.endswith('es'):
        word = word[:-2]
    elif word.endswith('s'):
        word = word[:-1]
    return word

def normalize(text: str) -> List[str]:
    """
    Normalize text: lowercase, remove punctuation, split, filter stopwords/short words.
    Allow 2-char words if they look like acronyms (e.g., 'AI', 'UX').
    """
    if not isinstance(text, str):
        raise ValueError("Input text must be a string.")
    if len(text) > 100000:  # Arbitrary limit for security (prevent DoS-like large inputs)
        raise ValueError("Text too long; limit is 100,000 characters.")
    
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)  # Remove non-alphanumeric/space
    tokens = text.split()
    filtered = []
    for t in tokens:
        if t in STOPWORDS:
            continue
        stemmed = simple_stem(t)
        if len(stemmed) > 2 or (len(stemmed) == 2 and (stemmed.isupper() or stemmed[0].isupper())):
            filtered.append(stemmed)
    return filtered

def extract_keywords(text: str, include_bigrams: bool = True) -> Set[str]:
    """
    Extract unique keywords, including optional bigrams for phrases.
    """
    tokens = normalize(text)
    keywords = set(tokens)  # Single words
    
    if include_bigrams and len(tokens) > 1:
        bigrams = {f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens)-1)}
        keywords.update(bigrams)
    
    return keywords

def ats_intelligence(resume_text: str, jd_text: str) -> Dict[str, any]:
    """
    ATS intelligence: Match resume keywords to JD, compute score, suggest improvements.
    
    Returns:
        dict with score (0-100), matched (list), missing (list), suggestions (list)
    """
    try:
        resume_keys = extract_keywords(resume_text)
        jd_keys = extract_keywords(jd_text)
        
        matched = sorted(resume_keys.intersection(jd_keys))
        missing = sorted(jd_keys.difference(resume_keys))
        
        score = 0
        if jd_keys:
            score = round((len(matched) / len(jd_keys)) * 100)
        
        suggestions = []
        for k in missing[:5]:
            suggestions.append(f"Consider adding experience or skills related to '{k}'.")
        
        return {
            "score": score,
            "matched": matched[:20],
            "missing": missing[:20],
            "suggestions": suggestions
        }
    except Exception as e:
        raise RuntimeError(f"Error in ATS intelligence: {str(e)}")

# Example usage (for testing):
# result = ats_intelligence("Your resume text here", "Job description text here")
# print(result)