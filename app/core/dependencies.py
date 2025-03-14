from functools import lru_cache
from app.services.news_service import NewsService

@lru_cache()
def get_news_service() -> NewsService:
    """
    Create and return a cached instance of NewsService.
    The lru_cache decorator ensures we reuse the same instance.
    """
    return NewsService() 