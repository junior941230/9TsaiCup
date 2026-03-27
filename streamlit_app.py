import streamlit as st
import databaseSetup as db
import pandas as pd
import FinMindApi
import datetime

st.set_page_config(page_title="2026韭菜杯大賽", layout="wide")

password = st.secrets["PASSWORD"]
userList = ["業誠","盧柏穎","林泓佐","李雨威","徐加成","陳亮均"]

@st.cache_resource
def initFinMind():
    return FinMindApi.FinMindApi()

fm = initFinMind()

@st.cache_data(ttl=86400) # 每天更新一次即可
def getMarketInfo():
    p0050Start, pTaiexStart = fm.getStartDayPrice()
    p0050Now, pTaiexNow = fm.getNowPrice()
    h0050 = fm.getHistoryData("0050")
    hTaiex = fm.getHistoryData("TAIEX")
    return p0050Start, pTaiexStart, p0050Now, pTaiexNow, h0050, hTaiex

@st.cache_data
def loadStartData():
    price0050Start, priceTAIEXStart = fm.getStartDayPrice()
    return price0050Start, priceTAIEXStart

# --- 初始化資料 ---
price0050Start, priceTaiexStart, price0050Now, priceTaiexNow, history0050Datas, historyTaiexDatas = getMarketInfo()

st.title("2026韭菜杯大賽 - 資產追蹤系統")

#--- 顯示大盤指數資訊 ---
col1, col2 = st.columns(2)
with col1:
    sparklineData = historyTaiexDatas.set_index('date')['close']
    delta = (priceTaiexNow - priceTaiexStart) / priceTaiexStart * 100
    st.metric("TAIEX", f"{priceTaiexNow}" ,delta= f"{delta:.2f}% 比賽日至今", chart_data=sparklineData, chart_type="line", border=True)
with col2:
    sparklineData = history0050Datas.set_index('date')['close']
    delta = (price0050Now - price0050Start) / price0050Start * 100
    st.metric("0050", f"{price0050Now} NTD" ,delta= f"{delta:.2f}% 比賽日至今", chart_data=sparklineData, chart_type="line", border=True)

# --- 選手排行榜計算 ---
userPerformance = []

for user in userList:
    cReturn, delta = db.getCumulativeReturn(user)
    userPerformance.append({"name": user, "return": cReturn, "delta": delta})

# 排序
userPerformance.sort(key=lambda x: x["return"], reverse=True)

# --- 選手列表顯示 ---
st.subheader("選手即時戰況")
icons = {0: "icon/gold.png", 1: "icon/silver.png", 2: "icon/bronze.png", 5: "icon/poop.png"}
userListCorrect = ["葉誠","盧柏穎","林泓佐","李雨威","徐加城","陳亮均"]
with st.container(border=True):
    for i, p in enumerate(userPerformance):
        user = p["name"]
        with st.container(border=True):
            colIcon, colTitle= st.columns([0.01,0.5])
            if i in icons:
                colIcon.image(icons[i], width=40)

            colTitle.markdown(f"### 第 {i+1} 名：{userListCorrect[userList.index(user)]} 選手")
            # 取得最新資訊
            latestInfo = db.getLatestNavInfo(user)
            dfHistory = db.getNavHistoryDf(user)

            # 顯示關鍵指標
            col1, col2, col3,col4 = st.columns(4)
            with col1:
                st.metric("當前總資產", f"${latestInfo['totalValue']:,.0f}")
            with col2:
                st.metric("累積報酬率", f"{p['return']:.2f}%", f"{p['delta']:.2f}%")
            with col3:
                navDelta = 0
                if len(dfHistory) >= 2:
                    navDelta = latestInfo['nav'] - dfHistory.iloc[-2]['nav']
                st.metric("最新單位淨值", f"{latestInfo['nav']:.4f}", f"{navDelta:.4f}")
            with col4:  
                with st.popover("詳細數據與圖表"):
                    st.metric("當前總單位數", f"{latestInfo['totalUnits']:,.2f}")
                    st.divider()
                    st.subheader("淨值走勢圖 (真實投資績效)")
                    if not dfHistory.empty:
                        dfHistory['date'] = pd.to_datetime(dfHistory['date']).dt.strftime('%Y-%m-%d')
                        dfChart = dfHistory.set_index('date')
                        st.line_chart(dfChart['nav'])
                    else:
                        st.info("目前還沒有資料，請在左側更新您的第一筆資產。")

                    st.subheader("總資產成長走勢圖")
                    if not dfHistory.empty:
                        st.bar_chart(dfChart['totalValue'])


        

@st.dialog("新增資料")
def addDATA():
    st.subheader("1. 日期")
    date = st.date_input("資料日期", value=datetime.date.today())
    date = date.strftime("%Y-%m-%d %H:%M:%S")
    st.subheader("2. 選擇使用者")
    userListAdd = ["選擇使用者"] + userList
    currentUser = st.selectbox("使用者代號", options=userListAdd)
    st.subheader("3. 資金進出")
    st.caption("是否有存入新資金，或領出資金？(若無請維持 0)")
    flowAmount = st.number_input("資金異動 (存入為正，領出為負)", value=0.0, step=1000.0)

    st.subheader("4. 現值")
    st.caption("請輸入目前各項資產的最新價值(入金後的市值)。")
    value = st.number_input("現金/存款", min_value=0.0, value=0.0, step=1000.0)

    if st.button("更新資料"):
        if currentUser == "選擇使用者":
            st.error("請選擇一位使用者。")
            return
        newAssets = [
            {'name': '總值', 'value': value},
        ]
        db.updateAssetsAndNav(date,currentUser, newAssets, flowAmount)
        st.success("資料已更新！")
        st.rerun()


passwordInput = st.text_input("請輸入密碼以驗證身份", type="password", key="password_input")
if st.button("新增資料"):
    if passwordInput == password:
        addDATA()
    else:
        st.error("密碼錯誤，無法新增資料。")

col1, col2= st.columns([0.3,0.7])
with col1:
    st.image("icon/1.png", width=200)
with col2:
    st.image("icon/2.png", width=200)