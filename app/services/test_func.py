import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from news_service import NewsService

async def test_news_service():
    """
    Test script to demonstrate NewsService functionality.
    Make sure you have .env file with required API keys before running this script.
    """
    try:
        # Load environment variables
        load_dotenv()
        
        # Create NewsService instance
        news_service = NewsService()

        # # Test fetch_article_content
        # url = "https://www.reuters.com/article/us-nvidia-idUSKBN2L828U"
        # content = await news_service.fetch_article_content(url)
        # print(f"Content: {content}")
        
        # Test parameters
        symbol = "NVDA"  # NVIDIA stock symbol
        date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")  # Last 7 days
        
        print(f"\n{'='*50}")
        print("Testing NewsService Functionality")
        print(f"{'='*50}")
        
        # Test query creation
        print("\n1. Testing search query creation:")
        query = news_service.create_search_query(symbol, date)
        print(f"Generated query: {query}")
        
        # Test news search
        print("\n2. Testing news search:")
        news_items = await news_service.search_news(query)
        print(f"Found {len(news_items)} news articles")
        for i, item in enumerate(news_items, 1):
            print(f"\nArticle {i}:")
            print(f"Title: {item['title']}")
            print(f"Link: {item['link']}")
            print(f"Content length: {len(item['content'])} characters")
        
        # Test news summarization
        print("\n3. Testing news summarization:")
        if news_items:
            summary = await news_service.summarize_news(news_items)
            print("\nSummary of news articles:")
            print(summary)
        
        # # Test complete workflow
        # print("\n4. Testing complete search and summarize workflow:")
        # result = await news_service.search_and_summarize(symbol)
        # print("\nFinal result:")
        # print(f"Summary: {result['summary']}")
        # print("\nSources:")
        # for source in result['sources']:
        #     print(f"- {source}")
            
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise

if __name__ == "__main__":
    # Run the async test function
    asyncio.run(test_news_service()) 