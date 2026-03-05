from FinMind.data import DataLoader
import streamlit as st
token = st.secrets["FINMINDTOKEN"]
api = DataLoader()
api.login_by_token(api_token=token)