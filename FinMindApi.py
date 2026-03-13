from FinMind.data import DataLoader
import streamlit as st
import datetime
import pandas as pd

class FinMindApi:
    def __init__(self):
        # 建議在進入點使用 st.cache_resource 呼叫，避免重複登入
        self.token = st.secrets["FINMINDTOKEN"]
        self.api = DataLoader()
        self.api.login_by_token(api_token=self.token)
        self.startDate = '2026-03-03'

    def getAdjustedDate(self):
        """計算符合台股交易時間的最新日期"""
        currentTime = datetime.datetime.now()
        adjustedDate = currentTime.date()
        
        # 台股收盤時間基準點 13:30
        targetTime = datetime.time(13, 30)
        
        # 尚未收盤則看前一天
        if currentTime.time() < targetTime:
            adjustedDate -= datetime.timedelta(days=1)
            
        # 處理假日（退回上一個週五）
        if adjustedDate.weekday() == 5:  # 星期六
            adjustedDate -= datetime.timedelta(days=1)
        elif adjustedDate.weekday() == 6:  # 星期日
            adjustedDate -= datetime.timedelta(days=2)
            
        return adjustedDate.strftime("%Y-%m-%d")

    def getStartDayPrice(self):
        """取得比賽起始日的價格"""
        # 0050
        df0050 = self.api.taiwan_stock_daily(
            stock_id='0050',
            start_date=self.startDate,
            end_date=self.startDate
        )
        # TAIEX
        dfTaiex = self.api.taiwan_stock_daily(
            stock_id="TAIEX", 
            start_date=self.startDate,
            end_date=self.startDate
        )
        
        # 若當天剛好沒資料（如遇假日），改抓起始日後第一筆
        price0050Start = df0050["close"].values[0] if not df0050.empty else 0
        priceTaiexStart = dfTaiex["close"].values[0] if not dfTaiex.empty else 0
        
        return price0050Start, priceTaiexStart
    
    def getNowPrice(self):
        """取得最新的收盤價格"""
        today = self.getAdjustedDate()
        
        # 抓取最近期的資料
        df0050 = self.api.taiwan_stock_daily(stock_id='0050', start_date=today)
        dfTaiex = self.api.taiwan_stock_daily(stock_id='TAIEX', start_date=today)
        
        # 取得最後一筆成交價
        price0050Now = df0050.iloc[-1]["close"] if not df0050.empty else 0
        priceTaiexNow = dfTaiex.iloc[-1]["close"] if not dfTaiex.empty else 0
        
        return price0050Now, priceTaiexNow
    
    def getHistoryData(self, stockId):
        """取得比賽至今的歷史走勢"""
        today = self.getAdjustedDate()
        df = self.api.taiwan_stock_daily(
            stock_id=stockId,
            start_date=self.startDate,
            end_date=today
        )
        return df