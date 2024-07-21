import streamlit as st
from langchain.llms import OpenAI
from langchain.agents import create_csv_agent
import pandas as pd

st.title('⚽️ José: Your AI Football Analyst ⚽️')

openai_api_key = st.sidebar.text_input('Enter your OpenAI API key here!', type='password')
