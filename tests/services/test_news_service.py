import pytest
from unittest.mock import Mock, patch
from aioresponses import aioresponses
from bs4 import BeautifulSoup
from app.services.news_service import NewsService

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to set up mock environment variables."""
    monkeypatch.setenv("GOOGLE_API_KEY", "mock_google_key")
    monkeypatch.setenv("GOOGLE_CSE_ID", "mock_cse_id")
    monkeypatch.setenv("OPENAI_API_KEY", "mock_openai_key")

@pytest.fixture
def news_service(mock_env_vars):
    """Fixture to create a NewsService instance with mock environment variables."""
    return NewsService()

def test_create_search_query(news_service):
    """Test the create_search_query method."""
    symbol = "NVDA"
    date = "2024-02-20"
    query = news_service.create_search_query(symbol, date)
    
    # Check if all components are present in the query
    assert '("NVDA" OR "NVIDIA Corporation")' in query
    assert "stock news" in query
    assert "earnings" in query
    assert "-site:youtube.com" in query
    assert "site:finance.yahoo.com" in query
    assert "after: 2024-02-20" in query
    assert "filetype:html" in query

@pytest.mark.asyncio
async def test_fetch_article_content():
    """Test the fetch_article_content method."""
    news_service = NewsService()
    mock_html = """
    <html>
        <body>
            <article>
                <p>Test paragraph 1</p>
                <p>Test paragraph 2</p>
            </article>
            <script>Some script</script>
            <style>Some style</style>
        </body>
    </html>
    """
    
    with aioresponses() as m:
        m.get('http://test.com', status=200, body=mock_html)
        content = await news_service.fetch_article_content('http://test.com')
        
        assert "Test paragraph 1" in content
        assert "Test paragraph 2" in content
        assert "Some script" not in content
        assert "Some style" not in content

@pytest.mark.asyncio
async def test_search_news(news_service):
    """Test the search_news method."""
    mock_search_results = {
        "items": [
            {
                "title": "Test News 1",
                "link": "http://test1.com",
            },
            {
                "title": "Test News 2",
                "link": "http://test2.com",
            }
        ]
    }
    
    # Mock the Google API client
    with patch('googleapiclient.discovery.build') as mock_build:
        mock_service = Mock()
        mock_cse = Mock()
        mock_list = Mock()
        mock_execute = Mock(return_value=mock_search_results)
        
        mock_build.return_value = mock_service
        mock_service.cse.return_value = mock_cse
        mock_cse.list.return_value = mock_list
        mock_list.execute = mock_execute
        
        # Mock the article content fetching
        with aioresponses() as m:
            m.get('http://test1.com', status=200, body='<article><p>Content 1</p></article>')
            m.get('http://test2.com', status=200, body='<article><p>Content 2</p></article>')
            
            results = await news_service.search_news("test query")
            
            assert len(results) == 2
            assert results[0]["title"] == "Test News 1"
            assert "Content 1" in results[0]["content"]
            assert results[1]["title"] == "Test News 2"
            assert "Content 2" in results[1]["content"]

@pytest.mark.asyncio
async def test_summarize_news(news_service):
    """Test the summarize_news method."""
    mock_news_items = [
        {
            "title": "Test News 1",
            "content": "Test content 1",
            "link": "http://test1.com"
        },
        {
            "title": "Test News 2",
            "content": "Test content 2",
            "link": "http://test2.com"
        }
    ]
    
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test summary"))]
    
    with patch.object(news_service.openai_client.chat.completions, 'create',
                     return_value=mock_response):
        summary = await news_service.summarize_news(mock_news_items)
        assert summary == "Test summary"

@pytest.mark.asyncio
async def test_search_and_summarize(news_service):
    """Test the search_and_summarize method."""
    mock_news_items = [
        {
            "title": "Test News 1",
            "content": "Test content 1",
            "link": "http://test1.com"
        }
    ]
    
    # Mock the dependent methods
    with patch.object(news_service, 'create_search_query',
                     return_value="test query"), \
         patch.object(news_service, 'search_news',
                     return_value=mock_news_items), \
         patch.object(news_service, 'summarize_news',
                     return_value="Test summary"):
        
        result = await news_service.search_and_summarize("NVDA")
        
        assert result["summary"] == "Test summary"
        assert result["sources"] == ["http://test1.com"]

@pytest.mark.asyncio
async def test_empty_search_results(news_service):
    """Test handling of empty search results."""
    with patch.object(news_service, 'search_news', return_value=[]):
        result = await news_service.search_and_summarize("INVALID")
        assert result["summary"] == "No news articles found."
        assert result["sources"] == []

@pytest.mark.asyncio
async def test_error_handling(news_service):
    """Test error handling in the news service."""
    with patch.object(news_service, 'search_news',
                     side_effect=Exception("API Error")), \
         pytest.raises(Exception) as exc_info:
        await news_service.search_and_summarize("NVDA")
        assert "API Error" in str(exc_info.value) 