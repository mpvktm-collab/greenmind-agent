# -*- coding: utf-8 -*-
import sys
import os
import time
import random
from langchain.tools import BaseTool
from typing import Optional
from langchain.callbacks.manager import CallbackManagerForToolRun

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class WebSearchTool(BaseTool):
    """Tool for searching current environmental news and information."""

    name: str = "Web_Search"
    description: str = "Searches the web for current environmental news and information."

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            time.sleep(random.uniform(1, 2))

            from ddgs import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))

            if not results:
                return "No web search results found. Please try a different query."

            lines = [f"Search Results for: \"{query}\"\n", "-" * 50]
            for i, r in enumerate(results, 1):
                title = r.get("title", "No title").strip()
                body = r.get("body", "No summary available.").strip()
                href = r.get("href", "")

                lines.append(f"\n{i}. {title}")
                lines.append(body)
                if href:
                    lines.append(f"Source: {href}")

            lines.append("\n" + "-" * 50)
            lines.append("Results from web search. For detailed analysis ask GreenMind directly.")

            return "\n".join(lines)

        except Exception as e:
            error_msg = str(e)
            if "Ratelimit" in error_msg or "rate" in error_msg.lower():
                return (
                    "Search is temporarily unavailable due to rate limits. "
                    "Please try again in a minute."
                )
            return "Web search temporarily unavailable. Please try again later."

    async def _arun(self, query: str) -> str:
        return self._run(query)


class WikipediaTool(BaseTool):
    """Tool for searching Wikipedia for environmental topics."""

    name: str = "Wikipedia_Knowledge"
    description: str = "Searches Wikipedia for environmental topics."

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            import wikipediaapi
            wiki = wikipediaapi.Wikipedia(language='en', user_agent='GreenMindAgent/1.0')

            clean_query = query.lower()
            for phrase in ["tell me about", "what is", "wikipedia"]:
                clean_query = clean_query.replace(phrase, "").strip()

            page = wiki.page(clean_query.title())

            if page.exists():
                summary = page.summary[:1500]
                return f"Wikipedia - {page.title}\n\n{summary}...\n\nSource: {page.fullurl}"
            return f"No Wikipedia page found for '{query}'."

        except Exception as e:
            return f"Wikipedia search error: {str(e)}"

    async def _arun(self, query: str) -> str:
        return self._run(query)
 