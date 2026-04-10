# GreenMind - Environmental Sustainability Advisor

An AI-powered environmental advisor that helps users understand and protect our planet.

## Features

- **Environmental Policies** - Query policies from various countries
- **Environmental Effects** - Learn about degradation causes and impacts
- **Pollution Index** - Check air quality and health indices for any location
- **Carbon Footprint** - Calculate emissions for activities and cities
- **Sustainability Tips** - Get practical eco-friendly advice
- **City Comparisons** - Compare pollution and carbon footprints across cities

## Technology Stack

- **Frontend**: Streamlit
- **Framework**: LangChain
- **LLM**: Google Gemini
- **Vector DB**: FAISS
- **Search**: DuckDuckGo, Wikipedia
- **MCP**: Model Context Protocol

## Prerequisites

- **Python 3.11.8** (strictly required - other versions may cause compatibility issues)
- Google Gemini API key - get it from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/greenmind.git
   cd greenmind

Project Structure:

greenmind/
├── src/
│   ├── agent.py              # Main agent
│   ├── tools/                 # Tool implementations
│   │   ├── rag_tools.py       # RAG tools for policies/effects
│   │   ├── web_search.py      # Web and Wikipedia search
│   │   ├── pollution_index.py # Air quality tool
│   │   ├── extra_tools.py     # Carbon footprint & tips
│   │   └── batch_scraper.py   # Web scraping utility
│   ├── database/              # Vector store
│   │   └── vector_store.py    # FAISS integration
│   ├── utils/                 # Logging
│   │   └── logger.py          # Logging functionality
│   ├── mcp/                   # MCP server implementation
│   │   ├── servers/           
│   │   ├── adapters/          
│   │   ├── protocol/          
│   │   └── client/            
│   └── data/                  # Document storage
│       ├── policies/          # Policy PDF documents
│       └── effects/           # Effects PDF documents
├── app.py                      # Streamlit UI
├── greenmind_mcp.py             # MCP server launcher
├── build_vector_stores.py       # Vector store builder utility
├── config.py                    # Configuration
├── url_policies.txt             # Policy URLs for scraping
├── url_effects.txt              # Effects URLs for scraping
├── requirements.txt             # Dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
