from typing import Dict, List
import os
from googleapiclient.discovery import build
from openai import AsyncOpenAI
from fastapi import HTTPException

class NewsService:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if not all([self.google_api_key, self.google_cse_id, os.getenv("OPENAI_API_KEY")]):
            raise ValueError("Missing required API keys in environment variables")

    def create_search_query(self, symbol: str) -> str:
        """Create a search query for the stock symbol."""
        return f"{symbol} stock news financial analysis latest"

    def search_news(self, query: str) -> List[Dict]:
        """Search for news using Google Custom Search API."""
        try:
            service = build("customsearch", "v1", developerKey=self.google_api_key)
            result = service.cse().list(q=query, cx=self.google_cse_id, num=5).execute()
            
            if "items" not in result:
                return []
            
            return [
                {
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "link": item.get("link", "")
                }
                for item in result["items"]
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Google search failed: {str(e)}")

    async def summarize_news(self, news_items: List[Dict]) -> str:
        """Summarize news articles using OpenAI's API."""
        if not news_items:
            return "No news articles found."

        # Prepare the content for summarization
        content = "\n\n".join([
            f"Title: {item['title']}\nSummary: {item['snippet']}"
            for item in news_items
        ])

        prompt = f"Please provide a concise summary of the following stock-related news:\n\n{content}\n\nSummary:"

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial news analyst. Provide clear and concise summaries of stock-related news."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"News summarization failed: {str(e)}")

    async def search_and_summarize(self, symbol: str) -> Dict:
        """Combine search and summarization into a single operation."""
        query = self.create_search_query(symbol)
        news_items = self.search_news(query)
        summary = await self.summarize_news(news_items)
        
        return {
            "summary": summary,
            "sources": [item["link"] for item in news_items]
        } 