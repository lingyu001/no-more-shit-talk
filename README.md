# Stock Market Analysis API

A FastAPI-based REST API for stock market analysis and news search.

## Features

- Stock news search with Google Search API and OpenAI summarization
- Market analysis capabilities (in development)
- Docker support for easy deployment
- Clean and maintainable architecture

## Setup

1. Clone the repository
2. Create a `.env` file with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_CSE_ID=your_google_custom_search_engine_id
   ```
3. Build and run with Docker:
   ```bash
   docker build -t stock-market-api .
   docker run -p 8000:8000 stock-market-api
   ```

Or run locally:
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### POST /stock_news_search
Search and summarize news for a given stock symbol.

### POST /market_analysis
Analyze market data for a given stock symbol (in development).

## Testing UI

A simple web UI for testing the API is available at `/static/index.html` when running the server. 