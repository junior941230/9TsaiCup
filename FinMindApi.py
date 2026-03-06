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
    
    def getAdjustedDate(self):
        currentTime = datetime.datetime.now()
        adjustedDate = currentTime.date()
        
        # 設定時間基準點為 1:30 (若你的 1.30 指的是下午 1:30，請將參數改為 13, 30)
        targetTime = datetime.time(1, 30)
        
        # 條件一：如果還沒到當天的 1:30，日期減去一天變成昨天
        if currentTime.time() < targetTime:
            adjustedDate -= datetime.timedelta(days=1)
            
        # 條件二：如果是假日，則退回上一個工作日 (星期五)
        # weekday() 回傳值：0 是星期一 ... 5 是星期六，6 是星期日
        if adjustedDate.weekday() == 5:
            adjustedDate -= datetime.timedelta(days=1)
        elif adjustedDate.weekday() == 6:
            adjustedDate -= datetime.timedelta(days=2)
            
        return adjustedDate.strftime("%Y-%m-%d")

    def getNowPrice(self):
        today = self.getAdjustedDate()
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
        today = self.getAdjustedDate()
        df = self.api.taiwan_stock_daily(
            stock_id=stock_id,
            start_date='2026-03-03',
            end_date=today
        )
        return df