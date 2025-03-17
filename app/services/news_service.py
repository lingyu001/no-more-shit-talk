from typing import Dict, List
import os
import httpx
from bs4 import BeautifulSoup
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

    def create_search_query(self, symbol: str, date: str) -> str:
        """Create a search query for the stock symbol."""
        query = '("NVDA" OR "NVIDIA Corporation") ("stock news" OR "earnings" OR "company news")'
        excluded_sites = "-site:youtube.com -site:facebook.com -site:tiktok.com -site:instagram.com -site:reddit.com -site:cnbc.com"
        included_sites = ""
        date_filter = f"after: {date}"
        file_type = "filetype:html"
        return f"{query} {excluded_sites} ({included_sites}) {date_filter} {file_type}"

    async def fetch_article_content(self, url: str) -> str:
        """Fetch and extract the main content of an article."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                    script.decompose()

                # Extract text from article or main content
                article = soup.find('article') or soup.find('main') or soup.find('body')
                if article:
                    # Get all paragraphs
                    paragraphs = article.find_all('p')
                    content = ' '.join(p.get_text().strip() for p in paragraphs)
                    # Clean up whitespace
                    content = ' '.join(content.split())
                    return content[:1000]  # Limit content length
                return ""
        except Exception as e:
            print(f"Error fetching article content from {url}: {str(e)}")
            return ""

    async def search_news(self, query: str) -> List[Dict]:
        """Search for news using Google Custom Search API and fetch article content."""
        try:
            service = build("customsearch", "v1", developerKey=self.google_api_key)
            result = service.cse().list(q=query, cx=self.google_cse_id, num=10).execute()
            
            if "items" not in result:
                return []
            
            news_items = []
            for item in result["items"]:
                content = await self.fetch_article_content(item.get("link", ""))
                if content:  # Only include articles where we successfully got content
                    news_items.append({
                        "title": item.get("title", ""),
                        "content": content,
                        "link": item.get("link", "")
                    })
            
            return news_items
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Google search failed: {str(e)}")

    async def summarize_news(self, news_items: List[Dict]) -> str:
        """Summarize news articles using OpenAI's API."""
        if not news_items:
            return "No news articles found."

        # Prepare the content for summarization
        content = "\n\n".join([
            f"Title: {item['title']}\nContent: {item['content']}"
            for item in news_items
        ])
        # write the content in to a file for dubugging
        with open("news_content_debug.txt", "w") as f:
            f.write(content)

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
        news_items = await self.search_news(query)
        summary = await self.summarize_news(news_items)
        
        return {
            "summary": summary,
            "sources": [item["link"] for item in news_items]
        } 