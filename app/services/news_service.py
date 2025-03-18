from typing import Dict, List
import os
import httpx
import yfinance as yf
from datetime import datetime, timedelta
from openai import AsyncOpenAI
from fastapi import HTTPException

class NewsService:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("Missing OpenAI API key in environment variables")

    async def fetch_article_content(self, url: str) -> str:
        """Fetch the full content of an article."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"Error fetching article content from {url}: {str(e)}")
            return ""

    async def get_news(self, symbol: str) -> List[Dict]:
        """Get news using yfinance API."""
        try:
            # Create a Ticker object
            ticker = yf.Ticker(symbol)
            
            # Get news
            news = ticker.news
            
            if not news:
                return []
            
            news_items = []
            for item in news[:10]:  # Take only the 10 most recent news items
                try:
                    if not isinstance(item, dict) or 'content' not in item:
                        continue
                        
                    content = item.get('content', {})
                    if not isinstance(content, dict):
                        continue
                    
                    # Extract the article content from the description or summary
                    article_content = content.get('description', '') or content.get('summary', '')
                    
                    # Get timestamp from pubDate
                    timestamp = content.get('pubDate', '')
                    if timestamp:
                        try:
                            published_at = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
                        except ValueError:
                            published_at = datetime.now()
                    else:
                        published_at = datetime.now()
                    
                    # Get URL from either clickThroughUrl or canonicalUrl
                    url = ''
                    click_through = content.get('clickThroughUrl', {})
                    canonical = content.get('canonicalUrl', {})
                    if isinstance(click_through, dict):
                        url = click_through.get('url', '')
                    if not url and isinstance(canonical, dict):
                        url = canonical.get('url', '')
                    
                    # Get publisher info
                    provider = content.get('provider', {})
                    publisher = provider.get('displayName', '') if isinstance(provider, dict) else ''
                    
                    news_items.append({
                        "title": content.get('title', ''),
                        "content": article_content,
                        "link": url,
                        "publisher": publisher,
                        "published_at": published_at.isoformat()
                    })
                except Exception as e:
                    print(f"Error processing news item: {str(e)}")
                    continue
            
            return news_items
        except Exception as e:
            print(f"Debug - Error in get_news: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")

    async def summarize_news(self, news_items: List[Dict]) -> str:
        """Summarize news articles using a two-step process with OpenAI's API."""
        if not news_items:
            return "No news articles found."

        # Step 1: Analyze each article individually
        article_analyses = []
        for item in news_items:
            article_content = f"Title: {item['title']}\nPublisher: {item['publisher']}\nPublished At: {item['published_at']}\nContent: {item['content']}"
            
            prompt = f"""Analyze this news article and extract key information focusing on:
1. Company key events
2. Market impacts
3. Significant product developments

Article:
{article_content}

Provide a structured analysis with these key points."""

            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo-16k",
                    messages=[
                        {"role": "system", "content": "You are a financial news analyst. Analyze news articles and extract key information about company events, market impacts, and product developments."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
                article_analyses.append(response.choices[0].message.content.strip())
            except Exception as e:
                print(f"Error analyzing article: {str(e)}")
                continue

        if not article_analyses:
            return "Failed to analyze news articles."

        # Step 2: Create a concise, objective summary
        combined_analyses = "\n\n".join(article_analyses)
        
        final_prompt = f"""Based on the following detailed analyses of multiple news articles, create a concise, objective single-paragraph summary that highlights the most significant information about:
1. Key company events
2. Market impacts
3. Product developments

Detailed Analyses:
{combined_analyses}

Provide a focused, objective summary that emphasizes the most important information."""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a financial news analyst. Create concise, objective summaries that focus on the most significant information."},
                    {"role": "user", "content": final_prompt}
                ],
                max_tokens=500,
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"News summarization failed: {str(e)}")

    async def search_and_summarize(self, symbol: str) -> Dict:
        """Combine news fetching and summarization into a single operation."""
        news_items = await self.get_news(symbol)
        summary = await self.summarize_news(news_items)
        
        return {
            "summary": summary,
            "sources": [{"link": item["link"], "publisher": item["publisher"], "published_at": item["published_at"]} for item in news_items]
        } 