# src/tools/web_search.py
import sys
import os
from langchain.tools import BaseTool
from typing import Optional, Any
from langchain.callbacks.manager import CallbackManagerForToolRun
from duckduckgo_search import DDGS
import wikipediaapi
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class WebSearchTool(BaseTool):
    """Tool for searching current environmental news and information"""
    
    name: str = "Web_Search"
    description: str = """
    Searches the web for current environmental news, policies, and sustainability information. 
    Use this for recent developments, current events, and general facts about environmental topics.
    Input should be a specific search query.
    """
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                
            if results:
                response = "Here's what I found on the web:\n\n"
                for i, result in enumerate(results, 1):
                    response += f"{i}. {result['title']}\n"
                    response += f"   {result['body']}\n"
                    response += f"   Source: {result['href']}\n\n"
                return response
            else:
                return "No web search results found."
        except Exception as e:
            return f"Web search failed: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class WikipediaTool(BaseTool):
    """Tool for searching Wikipedia for environmental topics"""
    
    name: str = "Wikipedia_Knowledge"
    description: str = """
    Searches Wikipedia for environmental topics, policies, and scientific concepts.
    Use this ONLY when explicitly asked for Wikipedia or for well-known topics.
    Input should be a specific topic to search for.
    """
    
    wiki: Any = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            user_agent='GreenMindAgent/1.0'
        )
    
    def _clean_query(self, query):
        """Clean the query by removing common phrases"""
        clean_query = query.lower()
        clean_query = clean_query.replace("tell me about", "").strip()
        clean_query = clean_query.replace("what is", "").strip()
        clean_query = clean_query.replace("what's", "").strip()
        clean_query = clean_query.replace("explain", "").strip()
        clean_query = clean_query.replace("wikipedia", "").strip()
        clean_query = clean_query.replace("article on", "").strip()
        clean_query = clean_query.replace("information about", "").strip()
        clean_query = clean_query.replace("tell me", "").strip()
        clean_query = clean_query.replace("about", "").strip()
        return clean_query.strip()
    
    def _get_search_variations(self, query):
        """Generate search variations for better matching"""
        variations = []
        
        # Original cleaned query
        variations.append(query)
        
        # Proper case
        variations.append(query.title())
        
        # Add "United States" for US-specific acts
        if "clean air act" in query.lower() and "united states" not in query.lower():
            variations.append("Clean Air Act (United States)")
        
        # Add " (act)" for legislation
        if "act" in query.lower() and "(" not in query:
            variations.append(f"{query.title()} (act)")
        
        # Handle climate-related terms
        if "climate change" in query.lower():
            variations.append("Climate change")
            variations.append("Effects of climate change")
        
        # Handle pollution terms
        if "air pollution" in query.lower():
            variations.append("Air pollution")
            variations.append("Health effects of air pollution")
        
        return variations
    
    def _search_wikipedia_api(self, query):
        """Search Wikipedia using the API for better results"""
        try:
            response = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "srlimit": 3,
                    "format": "json"
                },
                timeout=5
            ).json()
            
            if response.get("query", {}).get("search"):
                results = []
                for result in response["query"]["search"]:
                    title = result["title"]
                    page = self.wiki.page(title)
                    if page.exists():
                        # Check if it's a disambiguation page
                        if "may refer to:" in page.summary[:200]:
                            # Skip disambiguation pages in search results
                            continue
                        results.append({
                            "title": title,
                            "summary": page.summary[:1000] + "..."
                        })
                return results
        except Exception as e:
            print(f"Wikipedia API search failed: {str(e)}")
        return []
    
    def _handle_disambiguation(self, term, original_query):
        """Handle disambiguation pages by finding the most relevant section"""
        page = self.wiki.page(term)
        if not page.exists():
            return f"No information found for '{original_query}'."
        
        # Special handling for Clean Air Act
        if "clean air act" in original_query.lower():
            # Try to get the US-specific page directly
            us_page = self.wiki.page("Clean Air Act (United States)")
            if us_page.exists():
                return f"Wikipedia article: Clean Air Act (United States)\n\n{us_page.summary[:2000]}..."
            
            # Also try UK version
            uk_page = self.wiki.page("Clean Air Act 1956")
            if uk_page.exists() and "uk" in original_query.lower() or "britain" in original_query.lower():
                return f"Wikipedia article: Clean Air Act 1956 (United Kingdom)\n\n{uk_page.summary[:2000]}..."
        
        # Special handling for other common acts
        if "clean water act" in original_query.lower():
            cwa_page = self.wiki.page("Clean Water Act")
            if cwa_page.exists():
                return f"Wikipedia article: Clean Water Act\n\n{cwa_page.summary[:2000]}..."
        
        if "endangered species act" in original_query.lower():
            esa_page = self.wiki.page("Endangered Species Act of 1973")
            if esa_page.exists():
                return f"Wikipedia article: Endangered Species Act of 1973\n\n{esa_page.summary[:2000]}..."
        
        # Try to find the most relevant section
        sections = page.sections
        relevant_sections = []
        
        # Look for sections related to the query
        query_words = original_query.lower().split()
        for section in sections[:10]:  # Check first 10 sections
            section_title = section.title.lower()
            if any(word in section_title for word in query_words if len(word) > 3):
                relevant_sections.append(section)
        
        if relevant_sections:
            # Return the first relevant section
            section = relevant_sections[0]
            return f"Wikipedia article: {term} - {section.title}\n\n{section.text[:1500]}..."
        
        # If no relevant sections, provide guidance
        return f"Wikipedia article: {term} (disambiguation page)\n\n{page.summary[:500]}...\n\nPlease specify which version you're interested in. For example:\n• 'Clean Air Act (United States)'\n• 'Clean Air Act 1956' (UK)\n• 'Clean Water Act'\n• 'Endangered Species Act'"
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        # Clean the query
        clean_query = self._clean_query(query)
        
        # If query is too short, return helpful message
        if len(clean_query) < 3:
            return "Please provide a more specific topic to search for."
        
        # Special handling for common environmental topics - check this FIRST
        common_topics = {
            "clean air act": "Clean Air Act (United States)",
            "clean air act us": "Clean Air Act (United States)",
            "clean air act usa": "Clean Air Act (United States)",
            "clean air act uk": "Clean Air Act 1956",
            "clean air act britain": "Clean Air Act 1956",
            "clean water act": "Clean Water Act",
            "endangered species act": "Endangered Species Act of 1973",
            "paris agreement": "Paris Agreement",
            "kyoto protocol": "Kyoto Protocol",
            "montreal protocol": "Montreal Protocol",
            "climate change": "Climate change",
            "global warming": "Global warming",
            "greenhouse effect": "Greenhouse effect",
            "ozone layer": "Ozone layer",
            "biodiversity": "Biodiversity",
            "deforestation": "Deforestation",
            "air pollution": "Air pollution",
            "water pollution": "Water pollution",
            "plastic pollution": "Plastic pollution",
            "renewable energy": "Renewable energy",
            "solar power": "Solar power",
            "wind power": "Wind power",
            "carbon footprint": "Carbon footprint",
            "sustainability": "Sustainability"
        }
        
        # Check if the query matches any common topics first
        query_lower = query.lower()
        for key, value in common_topics.items():
            if key in query_lower:
                page = self.wiki.page(value)
                if page.exists():
                    # Check if it's a disambiguation page
                    if "may refer to:" in page.summary[:200]:
                        # It's a disambiguation page - handle it
                        return self._handle_disambiguation(value, query)
                    return f"Wikipedia article: {page.title}\n\n{page.summary[:2000]}..."
        
        # Generate search variations
        search_variations = self._get_search_variations(clean_query)
        
        # Try each variation
        for term in search_variations:
            page = self.wiki.page(term)
            if page.exists():
                # Check if it's a disambiguation page
                if "may refer to:" in page.summary[:200]:
                    # It's a disambiguation page
                    return self._handle_disambiguation(term, query)
                return f"Wikipedia article: {page.title}\n\n{page.summary[:2000]}..."
        
        # If no exact match, try API search (skip disambiguation pages)
        api_results = self._search_wikipedia_api(clean_query)
        if api_results:
            response = f"Wikipedia search results for '{query}':\n\n"
            for i, result in enumerate(api_results, 1):
                response += f"{i}. {result['title']}\n"
                response += f"   {result['summary']}\n\n"
            return response
        
        return f"No Wikipedia page found for '{query}'. Try being more specific or ask about policies directly using the Environmental_Policies_RAG tool."
    
    async def _arun(self, query: str) -> str:
        return self._run(query)