import json
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent

from src.config import get_model
from src.agent.prompt import SYSTEM_PROMPT
from src.agent.extractor import extract_movie_request
from src.tools.movie_tool import MovieLookupTool
from src.schemas import MovieAttributes
from src.utils.formatter import ok_payload


PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

def build_agent() -> AgentExecutor:
    llm = ChatOpenAI(model=get_model(), temperature=0.0, max_retries=2)
    tool = MovieLookupTool()
    agent = create_tool_calling_agent(llm=llm, tools=[tool], prompt=PROMPT)
    return AgentExecutor(agent=agent, tools=[tool], verbose=False, handle_parsing_errors=True)

def _direct_lookup(tool: MovieLookupTool, title: str, year: str | None) -> Dict[str, Any]:
    print(f"Direct lookup: title={title}, year={year}")
    raw = tool.run(title=title, year=year)
    print(f"Direct lookup raw: {raw}")
    data = json.loads(raw)
    print(f"Direct lookup parsed: {data}")
    return data

def answer_user(query: str) -> Dict[str, Any]:

    extraction = extract_movie_request(query)
    print(f"Extraction result: {extraction}")

    if not extraction.is_movie_query:
        return {
            "status": "not_movie",
            "message": "It looks like you’re not asking about a movie. Try: Tell me about \"Inception\" (2010)."
        }
    if not extraction.title:
        return {
            "status": "need_title",
            "message": "Please provide the exact movie title (and year if known). Example: \"The Dark Knight\" (2008)."
        }

    agent = build_agent()
    agent_input = (
        f"User asked: {query}\n"
        f"Extracted title: {extraction.title}\n"
        f"Extracted year: {extraction.year or 'unknown'}\n"
        "If needed, call movie_lookup with these."
    )

    try:
        print(agent_input)
        result = agent.invoke({"input": agent_input})
        print("=="*100)
        print(result)
        print("=="*100)
        text = (result.get("output") or "").strip()
        print(f"Agent output: {text}")

        # TODO Direct lookup code needed here.

        data = json.loads(text)
        if data.get("status") == "ok":
            print("Direct lookup successful")
            movie = data["movie"]
            attrs = MovieAttributes(**movie)
            bullets = attrs.to_bullets()
            return {
                "status": "ok",
                "poster": movie.get("Poster"),
                "bullets": bullets,
                "raw": movie,
            }
        
        if data.get("status") == "ambiguous":
            return {"status": "ambiguous", "message": data.get("message", ""), "candidates": data.get("candidates", [])}
        if data.get("status") == "error":
            return {"status": "error", "message": data.get("message", "Lookup failed.")}
        return {"status": "not_found", "message": "No matching movie found."}

    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {e}"}
