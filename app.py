import os
from flask import Flask, render_template, request, jsonify
import yfinance as yf
from newsapi import NewsApiClient
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

def get_stock_data(ticker_symbol):
    """Get stock data for the last 60 days"""
    stock = yf.Ticker(ticker_symbol)
    hist = stock.history(period='60d')
    return hist

def get_stock_news(company_name):
    """Get recent news about the company"""
    news = newsapi.get_everything(
        q=company_name,
        language='en',
        sort_by='publishedAt',
        page_size=5
    )
    return news['articles']

def predict_trend(data):
    """Predict stock trend using simple linear regression"""
    df = data.copy()
    
    # Prepare data
    df['Date'] = range(len(df))
    X = df[['Date']].values
    y = df['Close'].values
    
    # Create and fit the model
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict next 5 days
    future_dates = np.array(range(len(df), len(df) + 5)).reshape(-1, 1)
    future_prices = model.predict(future_dates)
    
    return future_prices

def generate_recommendation(data, prediction):
    """Generate buy/sell recommendation based on trends"""
    current_price = data['Close'].iloc[-1]
    predicted_price = prediction[-1]
    
    price_change = ((predicted_price - current_price) / current_price) * 100
    
    if price_change > 5:
        return "Strong Buy", price_change
    elif price_change > 2:
        return "Buy", price_change
    elif price_change < -5:
        return "Strong Sell", price_change
    elif price_change < -2:
        return "Sell", price_change
    else:
        return "Hold", price_change

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    ticker = request.form['ticker']
    
    try:
        # Get stock data
        stock_data = get_stock_data(ticker)
        
        # Get company info
        stock = yf.Ticker(ticker)
        company_name = stock.info.get('longName', ticker)
        
        # Get news
        news = get_stock_news(company_name)
        
        # Generate prediction
        prediction = predict_trend(stock_data)
        
        # Generate recommendation
        recommendation, price_change = generate_recommendation(stock_data, prediction)
        
        # Create stock price chart
        fig = go.Figure()
        
        # Historical prices
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['Close'],
            name='Historical Price',
            line=dict(color='blue')
        ))
        
        # Predicted prices
        future_dates = pd.date_range(
            start=stock_data.index[-1],
            periods=6,
            freq='D'
        )[1:]
        
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=prediction,
            name='Predicted Price',
            line=dict(color='red', dash='dash')
        ))
        
        chart_json = fig.to_json()
        
        return jsonify({
            'status': 'success',
            'company_name': company_name,
            'current_price': float(stock_data['Close'].iloc[-1]),
            'recommendation': recommendation,
            'price_change': float(price_change),
            'chart_data': chart_json,
            'news': news
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True)
