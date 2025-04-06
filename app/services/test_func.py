import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from news_service import NewsService

async def test_news_service():
    """
    Test script to demonstrate NewsService functionality.
    Make sure you have .env file with OPENAI_API_KEY before running this script.
    """
    try:
        # Load environment variables
        load_dotenv()
        
        # Create NewsService instance
        news_service = NewsService()
        
        # Test parameters
        symbol = "NVDA"  # NVIDIA stock symbol
        
        print(f"\n{'='*50}")
        print("Testing NewsService Functionality")
        print(f"{'='*50}")
        
        # Test news fetching
        print("\n1. Testing news fetching:")
        news_items = await news_service.get_news(symbol)
        print(f"Found {len(news_items)} news articles")
        for i, item in enumerate(news_items, 1):
            print(f"\nArticle {i}:")
            print(f"Title: {item['title']}")
            print(f"Publisher: {item['publisher']}")
            print(f"Published At: {item['published_at']}")
            print(f"Link: {item['link']}")
            print(f"Content length: {len(item['content'])} characters")
        
        # Test news summarization
        print("\n2. Testing news summarization:")
        if news_items:
            summary = await news_service.summarize_news(news_items)
            print("\nSummary of news articles:")
            print(summary)
        
        # # Test complete workflow
        # print("\n3. Testing complete search and summarize workflow:")
        # result = await news_service.search_and_summarize(symbol)
        # print("\nFinal result:")
        # print(f"Summary: {result['summary']}")
        # print("\nSources:")
        # for source in result['sources']:
        #     print(f"- Publisher: {source['publisher']}")
        #     print(f"  Published At: {source['published_at']}")
        #     print(f"  Link: {source['link']}")
        #     print()
            
        # # Test with a well-known stock symbol
        # news = await news_service.get_news("AAPL")
        # print(f"\nFetched {len(news)} news items for AAPL:")
        # for i, item in enumerate(news, 1):
        #     print(f"\n{i}. Title: {item['title']}")
        #     print(f"   Publisher: {item['publisher']}")
        #     print(f"   Link: {item['link']}")
        #     print(f"   Published At: {item['published_at']}")
        #     print(f"   Content Preview: {item['content'][:100]}...")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise

if __name__ == "__main__":
    # Run the async test function
    asyncio.run(test_news_service()) 