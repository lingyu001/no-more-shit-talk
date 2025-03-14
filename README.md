# Stock Analysis App beta

A web-based stock analysis application that provides real-time stock analysis, news, and trading recommendations.

## Features

- Real-time stock price data using Yahoo Finance
- Latest news about the company using NewsAPI
- Price trend prediction using machine learning
- Buy/Sell recommendations based on predicted trends
- Interactive price charts with historical and predicted values
- Clean and modern user interface

## Setup

1. Clone this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Sign up for a free API key at [NewsAPI](https://newsapi.org/)
4. Create a `.env` file in the root directory and add your NewsAPI key:
   ```
   NEWS_API_KEY=your_news_api_key_here
   ```

## Usage

1. Run the Flask application:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to `http://localhost:5000`
3. Enter a stock symbol (e.g., AAPL, GOOGL, MSFT) and click "Analyze"
4. View the analysis results, including:
   - Historical and predicted price chart
   - Current price and predicted change
   - Trading recommendation
   - Recent news about the company

## Technical Details

- Backend: Python Flask
- Frontend: HTML, CSS, JavaScript
- Data Sources: Yahoo Finance API, NewsAPI
- Charts: Plotly.js
- Machine Learning: scikit-learn (Linear Regression for trend prediction)

## Note

This is a basic implementation for educational purposes. The predictions are based on simple linear regression and should not be used as the sole basis for making investment decisions.
