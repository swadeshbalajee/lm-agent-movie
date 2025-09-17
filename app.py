import streamlit as st
import os
import json
from dotenv import load_dotenv

from src.agent.builder import answer_user
from src.config import validate_env

load_dotenv()

st.markdown(
    """
    <style>
      .poster {
          border-radius: 12px;
          border: 1px solid rgba(255,255,255,0.08);
      }
      .chip {
          display: inline-block;
          padding: 6px 12px;
          margin: 4px 6px 0 0;
          border-radius: 100px;
          background: rgba(110,231,183,0.12);
          color: #CFFAFE;
          cursor: pointer;
          user-select: none;
          border: 1px solid rgba(110,231,183,0.28);
          font-size: 0.9rem;
      }
      .muted { color: #9BA4B5; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.set_page_config(page_title="Movie Agent", page_icon="🎬", layout="centered")
st.title("🎬 Movie Agent")


env_ok, env_err = validate_env()
if not env_ok:
    st.error(env_err)
    st.stop()


with st.expander("Quick Samples", expanded=True):
    cols = st.columns(3)
    examples = (
        "Tell me about the movie Vishwaroopam.",
        "Tell me about the movie Vikram",
        "What do you know about the movie Hey Ram?",
        "Give me information about the movie Panchathanthiram.",
        "What do can get on Unnai Pol oruvan?"
    )

    for i, e in enumerate(examples):
        with cols[i % 3]:
            if st.button(e, key=f"example_{i}", help="Click to use this example"):
                st.session_state["query"] = e.strip()

query = st.text_input("Ask about a movie", key="query", placeholder="E.g., Tell me about the movie Vishwaroopam.", label_visibility="collapsed")

run = st.button("Run", type="primary", use_container_width=True)

if run:
    with st.spinner("Thinking..."):
        result = answer_user(query)
    
    status = result.get("status", "error")

    if status == "not_movie":
        st.warning(result.get("message", "The query does not seem to be about a movie. Please try again with a movie-related question."))
    elif status == "need_title":
        st.info(result.get("message", "Could not find a movie title in your query. Please specify a movie title."))
    elif status == "ambiguous":
        st.warning(result.get("message"))
        candidates = result.get("candidates", [])
        st.markdown("These are some possible movie titles I found:")
        chips = []
        for c in candidates:
            label = f"{c.get('Title', '?')}, ({c.get('Year', '?')})"
            chips.append(label)
            st.markdown(f'<span class="chip">{label}</span>', unsafe_allow_html=True)
        
        st.caption("Type the exact movie title and year again and click Run.")

    elif status == "ok":
        poster = result.get("poster", None)
        bullets = result.get("bullets", "Unknown")

        with st.container():
            st.markdown('<div >', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            if poster and poster.startswith("http"):
                with c1:
                    st.image(poster, caption="Poster", use_container_width=True)
            with c2:
                st.markdown(bullets)
            st.markdown("</div>", unsafe_allow_html=True)

            with st.expander("Raw details (debug)"):
                st.json(result.get("raw", {}))
            
    else:
        st.error(result.get("message", "An error occurred. Please try again later."))
        with st.expander("Eror details (debug)"):
            st.json(result)
    


