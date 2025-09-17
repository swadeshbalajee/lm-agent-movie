import re
from langchain_openai import ChatOpenAI

from src.schemas import MovieProperties
from src.config import get_model

def heuristic_extract(query: str):
    year = None
    m_year = re.search(r"\b(19|20)\d{2}\b", query)
    if m_year:
        year = m_year.group(0)

    m_quote = re.search(r"[\"“”'‘’](.+?)[\"“”'‘’]", query)
    if m_quote:
        return m_quote.group(1).strip(), year

    m_after = re.search(r"\b(movie|film)\s+([A-Za-z0-9: \-.'!&]+)", query, re.I)
    if m_after:
        cand = m_after.group(2).strip()
        cand = re.sub(r"[\s.?!,:;]+$", "", cand)
        return (cand or None), year

    return None, year

def llm_extract(query: str) -> MovieProperties:
    llm = ChatOpenAI(model=get_model(), temperature=0)
    structured = llm.with_structured_output(MovieProperties)
    prompt = (
        "Extract whether the user is asking about a cinema film (not person/series), "
        "and the likely title and 4-digit year if stated.\n"
        "If the user misspelled the title, return the likely intended title with correct spelling.\n"
        f"User message: {query}"
    )
    return structured.invoke(prompt)

def extract_movie_request(query: str) -> MovieProperties:
    t, y = heuristic_extract(query)
    if t:
        return MovieProperties(is_movie_query=True, title=t, year=y, reason="heuristic")
    return llm_extract(query)
