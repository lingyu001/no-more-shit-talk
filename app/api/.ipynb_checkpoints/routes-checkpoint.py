from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.news_service import NewsService
from app.core.dependencies import get_news_service

router = APIRouter()

class StockSymbolRequest(BaseModel):
    symbol: str

class NewsResponse(BaseModel):
    summary: str
    sources: list[str]

class MarketAnalysisResponse(BaseModel):
    # To be implemented
    symbol: str
    status: str = "In development"

@router.post("/stock_news_search", response_model=NewsResponse)
async def search_stock_news(
    request: StockSymbolRequest,
    news_service: NewsService = Depends(get_news_service)
):
    """
    Search and summarize news for a given stock symbol.
    """
    try:
        news_results = await news_service.search_and_summarize(request.symbol)
        return NewsResponse(
            summary=news_results["summary"],
            sources=news_results["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/market_analysis", response_model=MarketAnalysisResponse)
async def analyze_market(request: StockSymbolRequest):
    """
    Analyze market data for a given stock symbol (to be implemented).
    """
    return MarketAnalysisResponse(symbol=request.symbol) 