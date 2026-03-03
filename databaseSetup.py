import pandas as pd
from datetime import datetime
from pymongo import MongoClient
import certifi
import streamlit as st

# 取得連線設定
mongoUri = st.secrets["MONGO_URI"]
dbName = st.secrets["DB_NAME"]

# 建立連線
client = MongoClient(mongoUri, tlsCAFile=certifi.where())
db = client[dbName]

# 指定 Collection (集合)
assetsDetailCol = db['assetsDetail']
capitalFlowCol = db['capitalFlow']
navHistoryCol = db['navHistory']

def getLatestNavInfo(userId):
    """取得特定使用者最新的淨值、總單位數、總價值"""
    # 依據 date 降序排列，取最新一筆
    latestRecord = navHistoryCol.find_one({'userId': userId}, sort=[('date', -1)])
    
    if not latestRecord:
        return {'totalValue': 0, 'totalUnits': 0, 'nav': 0}
    return {
        'totalValue': latestRecord['totalValue'],
        'totalUnits': latestRecord['totalUnits'],
        'nav': latestRecord['nav']
    }

def updateAssetsAndNav(userId, newAssetData, flowAmount):
    """
    userId: 區別不同使用者的 ID
    newAssetData: [{'name': '現金', 'value': 50000}, ...]
    flowAmount: 存入為正，領出為負。若只有市值變動則為 0。
    """
    currentDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. 計算當前總價值
    newTotalValue = sum(item['value'] for item in newAssetData)

    # 2. 取得前次紀錄
    lastInfo = getLatestNavInfo(userId)
    lastNav = lastInfo['nav']
    lastUnits = lastInfo['totalUnits']

    # 3. 單位淨值邏輯計算
    if lastNav == 0:
        # 第一次投入
        newNav = 100.0
        newUnits = newTotalValue / newNav if newNav > 0 else 0
    else:
        if flowAmount != 0:
            # 有資金進出：根據前次淨值計算新增/減少的單位數
            addedUnits = flowAmount / lastNav
            newUnits = lastUnits + addedUnits
            # 新淨值 = 新總價值 / 新單位數
            newNav = newTotalValue / newUnits if newUnits > 0 else 0
        else:
            # 沒有資金進出，純粹資產漲跌：單位數不變，淨值改變
            newUnits = lastUnits
            newNav = newTotalValue / newUnits if newUnits > 0 else 0

    # 4. 寫入資料庫
    # 寫入資產明細
    for item in newAssetData:
        assetsDetailCol.insert_one({
            'userId': userId,
            'date': currentDate,
            'value': item['value']
        })
    
    # 寫入資金異動 (若有)
    if flowAmount != 0:
        capitalFlowCol.insert_one({
            'userId': userId,
            'date': currentDate,
            'flowAmount': flowAmount
        })

    # 寫入淨值歷史
    navHistoryCol.insert_one({
        'userId': userId,
        'date': currentDate,
        'totalValue': newTotalValue,
        'totalUnits': newUnits,
        'nav': newNav
    })

def getNavHistoryDf(userId):
    """取得特定使用者的歷史淨值 DataFrame"""
    cursor = navHistoryCol.find({'userId': userId}, {'_id': 0, 'date': 1, 'nav': 1, 'totalValue': 1}).sort('date', 1)
    records = list(cursor)
    if not records:
        return pd.DataFrame(columns=['date', 'nav', 'totalValue'])
    return pd.DataFrame(records)

def getCumulativeReturn(userId):
    """計算特定使用者的總報酬率"""
    # 取得第一筆紀錄 (初始值)
    firstRecord = navHistoryCol.find_one({'userId': userId}, sort=[('date', 1)])
    # 取得最新一筆紀錄
    secondRecord = navHistoryCol.find_one({'userId': userId}, sort=[('date', -1)], skip=1)
    latestRecord = navHistoryCol.find_one({'userId': userId}, sort=[('date', -1)])
    
    if not firstRecord or not latestRecord:
        return 0.0,0.0  # 沒有資料或只有一筆資料，報酬率為 0
    
    initialNav = firstRecord['nav']
    if secondRecord:
        secondNav = secondRecord['nav'] 
    else:
        secondNav = initialNav
    currentNav = latestRecord['nav']

    

    if initialNav == 0:
        return 0.0,0.0
        
    cumulativeReturn = ((currentNav - initialNav) / initialNav) *100
    delta = cumulativeReturn - (((secondNav - initialNav) / initialNav) *100)
    return cumulativeReturn , delta