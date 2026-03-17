# app.py - Complete version with HTTP based MCP Server
import streamlit as st
import sys
import os
import asyncio
import re
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.mcp.client.mcp_client import MCPClient

# ------------------------------------------------------------
# MCP Configuration
# ------------------------------------------------------------

MCP_HOST = os.getenv("MCP_HOST", "greenmind-mcp.onrender.com")

# ------------------------------------------------------------
# Streamlit Page Setup
# ------------------------------------------------------------

st.set_page_config(
    page_title="GreenMind - Environmental Sustainability Advisor",
    layout="wide"
)

# ------------------------------------------------------------
# Session State Initialization
# ------------------------------------------------------------

if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = None
    st.session_state.mcp_connected = False

if "messages" not in st.session_state:

    quotes = [
        {"text": "The earth is what we all have in common.", "author": "Wendell Berry"},
        {"text": "The environment is where we all meet.", "author": "Lady Bird Johnson"},
        {"text": "We borrow the earth from our children.", "author": "Native American Proverb"},
        {"text": "Look deep into nature and you will understand everything better.", "author": "Albert Einstein"},
        {"text": "In every walk with nature one receives far more than he seeks.", "author": "John Muir"}
    ]

    quote = quotes[datetime.now().day % len(quotes)]

    st.session_state.quote_data = quote

    st.session_state.messages = [{
        "role": "assistant",
        "content":
        "Hello. I am GreenMind, your environmental sustainability advisor.\n\n"
        "I can assist with:\n"
        "Environmental policies and regulations\n"
        "Environmental effects and impacts\n"
        "Pollution and environmental health indices\n"
        "Carbon footprint calculations\n"
        "Sustainability tips\n"
        "City comparisons\n\n"
        "How can I help you protect the environment today?"
    }]

# ------------------------------------------------------------
# MCP Client
# ------------------------------------------------------------

async def get_mcp_client():

    if st.session_state.mcp_client is None:

        client = MCPClient(host=MCP_HOST)

        try:
            connected = await client.connect()

            if connected:
                st.session_state.mcp_client = client
                st.session_state.mcp_connected = True
            else:
                st.session_state.mcp_connected = False

        except Exception:
            st.session_state.mcp_connected = False

    return st.session_state.mcp_client


async def call_mcp_tool(tool_name, query):

    client = await get_mcp_client()

    if client is None:
        return "MCP server connection failed."

    try:
        result = await client.call_tool(tool_name, input=query)
        return result

    except Exception as e:
        return f"Tool execution error: {str(e)}"


# ------------------------------------------------------------
# Response Cleaning
# ------------------------------------------------------------

def clean_response(text):

    if not isinstance(text, str):
        return text

    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# ------------------------------------------------------------
# Query Routing
# ------------------------------------------------------------

async def process_query_async(query):

    q = query.lower()

    if "policy" in q or "regulation" in q or "law" in q:
        tool = "Environmental_Policies_RAG"

    elif "effect" in q or "climate" in q or "impact" in q:
        tool = "Environmental_Effects_RAG"

    elif "pollution" in q or "aqi" in q:
        tool = "Pollution_Health_Index"

    elif "carbon" in q or "footprint" in q:
        tool = "Carbon_Footprint_Calculator"

    elif "tip" in q or "sustainable" in q:
        tool = "Sustainability_Tips"

    elif "news" in q or "search" in q:
        tool = "Web_Search"

    else:
        tool = "Environmental_Policies_RAG"

    result = await call_mcp_tool(tool, query)

    result = clean_response(result)

    return result, tool


def process_query(query):

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    result, tool = loop.run_until_complete(process_query_async(query))

    loop.close()

    return result, tool


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.title("GreenMind")
st.subheader("Environmental Sustainability Advisor")

# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------

with st.sidebar:

    st.header("About GreenMind")

    st.write(
        "GreenMind is an AI assistant designed to provide knowledge "
        "about environmental sustainability, policies, pollution data, "
        "and climate impacts."
    )

    st.markdown("---")

    st.subheader("MCP Server")

    st.write(f"Server: https://{MCP_HOST}")

    if st.button("Test MCP Connection"):

        async def test():
            client = MCPClient(host=MCP_HOST)
            return await client.connect()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        status = loop.run_until_complete(test())

        loop.close()

        if status:
            st.success("Connected")
        else:
            st.error("Connection failed")

    st.markdown("---")

    if st.session_state.mcp_connected:
        st.success("Server Connected")
    else:
        st.error("Server Disconnected")

    st.markdown("---")

    if st.button("Clear Conversation"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# ------------------------------------------------------------
# Display Quote
# ------------------------------------------------------------

with st.chat_message("assistant"):

    quote = st.session_state.quote_data

    st.markdown(f"""
    "{quote['text']}"
    
    - {quote['author']}
    """)

    st.markdown(st.session_state.messages[0]["content"])

# ------------------------------------------------------------
# Display Chat History
# ------------------------------------------------------------

for msg in st.session_state.messages[1:]:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ------------------------------------------------------------
# Chat Input
# ------------------------------------------------------------

prompt = st.chat_input("Ask about environmental sustainability")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Processing request..."):

            response, tool = process_query(prompt)

            st.markdown(response)

            st.caption(f"Tool used: {tool}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    st.rerun()


# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

st.markdown("---")

st.markdown(
    "GreenMind - Promoting sustainable environmental awareness."
)