from FinMind.data import DataLoader
import streamlit as st
import datetime
class FinMindApi:
    def __init__(self):
        token = st.secrets["FINMINDTOKEN"]
        self.api = DataLoader()
        self.api.login_by_token(api_token=token)

    def getStartDayPrice(self):
        df = self.api.taiwan_stock_daily(
            stock_id='0050',
            start_date='2026-03-03',
        )
        price0050Start = df["close"].values[0]
        df = self.api.taiwan_stock_daily(
            stock_id="TAIEX", 
            start_date='2026-03-03'
        )
        priceTAIEXStart = df["close"].values[0]
        
        return price0050Start, priceTAIEXStart
    
    def getNowPrice(self):
        today = datetime.date.today().strftime("%Y-%m-%d")
        df = self.api.taiwan_stock_daily(
            stock_id='0050',
            start_date=today,
        )
        price0050Now = df.tail(1)["close"].values[0]
        df = self.api.taiwan_stock_daily(
            stock_id='TAIEX',
            start_date=today,
        )
        priceTAIEXNow = df.tail(1)["close"].values[0]
        return price0050Now, priceTAIEXNow
    
    def getHistoryData(self, stock_id):
        today = datetime.date.today().strftime("%Y-%m-%d")
        df = self.api.taiwan_stock_daily(
            stock_id=stock_id,
            start_date='2026-03-03',
            end_date=today
        )
        return df