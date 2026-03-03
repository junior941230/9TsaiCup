import streamlit as st
import databaseSetup as db
import pandas as pd
password = st.secrets["PASSWORD"]
userList = ["業誠","盧柏穎","林泓佐","李雨威","徐加成","陳亮均"]
st.set_page_config(page_title="2026韭菜杯大賽", layout="wide")
st.title("2026韭菜杯大賽 - 資產追蹤系統")

cumulativeReturns = {}
for user in userList:
    cumulativeReturn, delta = db.getCumulativeReturn(user)
    cumulativeReturns[user] = cumulativeReturn
cumulativeReturns = dict(sorted(cumulativeReturns.items(), key=lambda item: item[1], reverse=True))

for i, user in enumerate(cumulativeReturns.keys()):
    with st.container(border=True):
        colIcon, colTitle= st.columns([0.01,0.5])
        if i == 0:
            colIcon.image("icon/gold.png", width=40)
        elif i == 1:
            colIcon.image("icon/silver.png", width=40)
        elif i == 2:
            colIcon.image("icon/bronze.png", width=40)
        elif i == 5:
            colIcon.image("icon/poop.png", width=40)

        colTitle.write(f"### {user} 選手")
        # 取得最新資訊
        latestInfo = db.getLatestNavInfo(user)
        dfHistory = db.getNavHistoryDf(user)
        cumulativeReturn, delta = db.getCumulativeReturn(user)
        # 顯示關鍵指標
        col1, col2, col3,col4 = st.columns(4)
        with col1:
            st.metric("當前總資產", f"${latestInfo['totalValue']:,.0f}")
        with col2:
            st.metric("報酬率", f"{cumulativeReturn:.2f}%", f"{delta:.2f}%")
        with col3:
            navDelta = 0
            if len(dfHistory) >= 2:
                navDelta = latestInfo['nav'] - dfHistory.iloc[-2]['nav']
            st.metric("最新單位淨值", f"{latestInfo['nav']:.4f}", f"{navDelta:.4f}")
        with col4:
            with st.popover("更多資訊"):
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
    st.subheader("1. 選擇使用者")
    currentUser = st.selectbox("使用者代號", options=userList)
    st.subheader("2. 資金進出")
    st.caption("是否有存入新資金，或領出資金？(若無請維持 0)")
    flowAmount = st.number_input("資金異動 (存入為正，領出為負)", value=0.0, step=1000.0)

    st.subheader("3.現值")
    st.caption("請輸入目前各項資產的最新價值")
    value = st.number_input("現金/存款", min_value=0.0, value=0.0, step=1000.0)

    if st.button("更新資料"):
        newAssets = [
            {'name': '總值', 'value': value},
        ]
        db.updateAssetsAndNav(currentUser, newAssets, flowAmount)
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