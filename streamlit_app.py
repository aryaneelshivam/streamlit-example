
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from tradingview_ta import TA_Handler, Interval, Exchange
import streamlit as st

# Function to fetch stock data based on user input
def load_stock_data(stock_symbol):
    start_date = "2022-01-01"
    end_date = pd.to_datetime("today").strftime('%Y-%m-%d')
    stock_data = yf.download(stock_symbol, start=start_date, end=end_date)
    return stock_data

# Function to calculate buy/sell signals
def buy_sell(stock_data):
    signalBuy = []
    signalSell = []
    position = False

    for i in range(len(stock_data)):
        if stock_data['SMA5'][i] > stock_data['SMA15'][i]:
            if position == False:
                signalBuy.append(stock_data['Adj Close'][i])
                signalSell.append(None)
                position = True
            else:
                signalBuy.append(None)
                signalSell.append(None)
        elif stock_data['SMA5'][i] < stock_data['SMA15'][i]:
            if position == True:
                signalBuy.append(None)
                signalSell.append(stock_data['Adj Close'][i])
                position = False
            else:
                signalBuy.append(None)
                signalSell.append(None)
        else:
            signalBuy.append(None)
            signalSell.append(None)
    return pd.Series([signalBuy, signalSell])

# Function to calculate buy/sell signals using EMA
def buy_sellema(stock_data):
    signalBuyema = []
    signalSellema = []
    position = False

    for i in range(len(stock_data)):
        if stock_data['EMA5'][i] > stock_data['EMA15'][i]:
            if position == False:
                signalBuyema.append(stock_data['Adj Close'][i])
                signalSellema.append(None)
                position = True
            else:
                signalBuyema.append(None)
                signalSellema.append(None)
        elif stock_data['EMA5'][i] < stock_data['EMA15'][i]:
            if position == True:
                signalBuyema.append(None)
                signalSellema.append(stock_data['Adj Close'][i])
                position = False
            else:
                signalBuyema.append(None)
                signalSellema.append(None)
        else:
            signalBuyema.append(None)
            signalSellema.append(None)
    return pd.Series([signalBuyema, signalSellema])

# Function to get recommendations data
def get_recommendations(symbol, screener, exchange, interval):
    stock = TA_Handler(
        symbol=symbol,
        screener=screener,
        exchange=exchange,
        interval=interval,
    )
    return stock.get_analysis().summary

# Streamlit app
def main():
    st.title("Stock Analysis App")

    st.sidebar.title("Tabs")
    tabs = ["Stock Analysis", "Recommendations"]
    current_tab = st.sidebar.radio("Select Tab", tabs)

    if current_tab == "Stock Analysis":
        st.header("Stock Price History with Buy/Sell Signals")

        # Text input for stock symbol
        stock_symbol = st.text_input("Enter Stock Symbol", "BEL.NS")

        stock_data = load_stock_data(stock_symbol)

        # Calculate buy/sell signals
        stock_data['EMA5'] = stock_data['Close'].ewm(span=5).mean()
        stock_data['EMA15'] = stock_data['Close'].ewm(span=15).mean()
        stock_data['SMA5'] = stock_data['Close'].rolling(window=5).mean()
        stock_data['SMA15'] = stock_data['Close'].rolling(window=15).mean()
        rstd = stock_data['Close'].rolling(window=15).std()
        upper_band = stock_data['SMA15'] + 2 * rstd
        lower_band = stock_data['SMA15'] - 2 * rstd

        stock_data[['Buy_Signal_price', 'Sell_Signal_price']] = buy_sell(stock_data)
        stock_data[['Buy_Signal_priceEMA', 'Sell_Signal_priceEMA']] = buy_sellema(stock_data)

        # Create figures for each graph
        price_chart = go.Figure(data=[
            go.Scatter(x=stock_data.index, y=stock_data['Adj Close'], mode='lines', name='Adj Close'),
            go.Scatter(x=stock_data.index, y=stock_data['SMA5'], mode='lines', name='SMA5'),
            go.Scatter(x=stock_data.index, y=stock_data['SMA15'], mode='lines', name='SMA15'),
            go.Scatter(x=stock_data.index, y=stock_data['EMA5'], mode='lines', name='EMA5'),
            go.Scatter(x=stock_data.index, y=stock_data['EMA15'], mode='lines', name='EMA15'),
            go.Scatter(x=stock_data.index, y=stock_data['Buy_Signal_price'], mode='markers', name='Buy SMA',
                       marker=dict(color='green', size=8)),
            go.Scatter(x=stock_data.index, y=stock_data['Sell_Signal_price'], mode='markers', name='Sell SMA',
                       marker=dict(color='red', size=8)),
            go.Scatter(x=stock_data.index, y=stock_data['Buy_Signal_priceEMA'], mode='markers', name='Buy E

MA',
                       marker=dict(color='black', size=8)),
            go.Scatter(x=stock_data.index, y=stock_data['Sell_Signal_priceEMA'], mode='markers', name='Sell EMA',
                       marker=dict(color='purple', size=8)),
            go.Scatter(x=stock_data.index, y=upper_band, mode='lines', name='Upper Bollinger Band'),
            go.Scatter(x=stock_data.index, y=lower_band, mode='lines', name='Lower Bollinger Band'),
        ])

        st.plotly_chart(price_chart, use_container_width=True)

        st.subheader("Stock Price Analysis Charts")
        st.sidebar.markdown("### Choose Analysis Chart")
        chart_option = st.sidebar.selectbox("Select Chart", ["Price Chart", "SMA Chart", "EMA Chart", "Bollinger Bands Chart", "Volume Chart"])

        if chart_option == "SMA Chart":
            price_chart_sma = go.Figure(data=[
                go.Scatter(x=stock_data.index, y=stock_data['Adj Close'], mode='lines', name='Adj Close'),
                go.Scatter(x=stock_data.index, y=stock_data['SMA5'], mode='lines', name='SMA5'),
                go.Scatter(x=stock_data.index, y=stock_data['SMA15'], mode='lines', name='SMA15'),
                go.Scatter(x=stock_data.index, y=stock_data['Buy_Signal_price'], mode='markers', name='Buy SMA',
                           marker=dict(color='green', size=8)),
                go.Scatter(x=stock_data.index, y=stock_data['Sell_Signal_price'], mode='markers', name='Sell SMA',
                           marker=dict(color='red', size=8)),
            ])

            st.plotly_chart(price_chart_sma, use_container_width=True)

        elif chart_option == "EMA Chart":
            price_chart_ema = go.Figure(data=[
                go.Scatter(x=stock_data.index, y=stock_data['Adj Close'], mode='lines', name='Adj Close'),
                go.Scatter(x=stock_data.index, y=stock_data['EMA5'], mode='lines', name='EMA5'),
                go.Scatter(x=stock_data.index, y=stock_data['EMA15'], mode='lines', name='EMA15'),
                go.Scatter(x=stock_data.index, y=stock_data['Buy_Signal_priceEMA'], mode='markers', name='Buy EMA',
                           marker=dict(color='black', size=8)),
                go.Scatter(x=stock_data.index, y=stock_data['Sell_Signal_priceEMA'], mode='markers', name='Sell EMA',
                           marker=dict(color='purple', size=8)),
            ])

            st.plotly_chart(price_chart_ema, use_container_width=True)

        elif chart_option == "Bollinger Bands Chart":
            price_chart_bb = go.Figure(data=[
                go.Scatter(x=stock_data.index, y=stock_data['Adj Close'], mode='lines', name='Adj Close'),
                go.Scatter(x=stock_data.index, y=stock_data['EMA5'], mode='lines', name='EMA5'),
                go.Scatter(x=stock_data.index, y=stock_data['EMA15'], mode='lines', name='EMA15'),
                go.Scatter(x=stock_data.index, y=upper_band, mode='lines', name='Upper Bollinger Band'),
                go.Scatter(x=stock_data.index, y=lower_band, mode='lines', name='Lower Bollinger Band'),
            ])

            st.plotly_chart(price_chart_bb, use_container_width=True)

        elif chart_option == "Volume Chart":
            volume_chart = go.Figure(data=[
                go.Scatter(x=stock_data.index, y=stock_data['Volume'], mode='lines', name='Volume',
                           line=dict(color='purple'))
            ])

            st.plotly_chart(volume_chart, use_container_width=True)

    elif current_tab == "Recommendations":
        st.header("Stock Recommendations")

        # Text input for stock symbol
        stock_symbol_recommendations = st.text_input("Enter Stock Symbol for Recommendations", "ZOMATO")

        symbol = stock_symbol_recommendations
        screener = "india"
        exchange = "NSE"
        interval = Interval.INTERVAL_1_MONTH
        recommendations = get_recommendations(symbol, screener, exchange, interval)

        # Convert recommendations to a Pandas DataFrame
        df = pd.DataFrame(recommendations, index=[0])

        # Extract the relevant columns for the pie chart, handling missing columns
        cols_to_plot = ['BUY', 'SELL', 'NEUTRAL', 'STRONG_BUY', 'STRONG_SELL']
        existing_cols = [col for col in cols_to_plot if col in df.columns]
        pie_data = df[existing_cols]

        # Plot the pie chart
        fig, ax = plt.subplots()
        pie_data.T.plot.pie(subplots=True, autopct='%1.1f%%', legend=False, startangle=90, ax=ax)
        ax.set_title(f'Recommendations for {symbol} on {exchange} - {interval}')

        st.pyplot(fig)

if __name__ == '__main__':
    main()
