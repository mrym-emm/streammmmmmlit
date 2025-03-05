import yfinance as yf
import streamlit as st

st.write(
    """
# Simple Stock Price App

Shown are the stock closing price & volume of 
<span style ="color: blue">G</span><span style ="color: red">o</span><span style ="color: green">o</span><span style ="color: blue">g</span><span style ="color: green">l</span><span style ="color: red">e</span>!
""",
    unsafe_allow_html=True,
)

# yfinance is open source python library that provides free acces to financial data on Yahoofinacne
ticker = "GOOG"

# get data from yfinance using the ticker defined
ticker_data = yf.Ticker(ticker)

print("hello")
tickerDf = ticker_data.history(period="1d", start="2010-5-31", end="2025-3-1")

st.write(
    """
         ### Closing price
         # """
)
st.line_chart(tickerDf.Close)

st.write(
    """
         ### Volume price
         # """
)
st.line_chart(tickerDf.Volume)
