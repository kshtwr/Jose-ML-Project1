import streamlit as st
from langchain.llms import OpenAI
from langchain_experimental.agents import create_csv_agent
import pandas as pd
from dotenv import load_dotenv
import os

st.set_page_config(page_title="⚽️ José: Your AI Football Analyst ⚽️")

def main():
    load_dotenv()
    if os.getenv("OPENAI_API_KEY") is None or os.getenv("OPENAI_API_KEY") == "":
        print("OPENAI_API_KEY is not set")
        exit(1)
    else:
        print("OPENAI_API_KEY is set")

    st.header("⚽️ José: Your AI Football Analyst ⚽️")
    
    option_names = ["Predictions", "Past Seasons"]
    option = st.radio("Choose to talk about the future or the past 3 seasons!", option_names, key="radio_option")
    
    database_csv = None
    if option == "Past Seasons":
        database_csv = "/Users/keshav/Documents/Projects/Jose_Buildspace/all_plmatches_23to20.csv"
    elif option == "Predictions":
        database_csv = "/Users/keshav/Documents/Projects/Jose_Buildspace/2024-25_predictions.csv"
   
    llm = OpenAI(temperature= 0)
    agent = create_csv_agent(llm, path=database_csv, verbose = True, allow_dangerous_code = True)
    rules = """
            You are Jose Mourinho, the football manager. \
            He is confident, passionate, nostalgic, verbose and arrogant. \
            Answer truthfully when it comes to statistics. \  
            Be arrogant in every sentence you say. \
            You support Chelsea but do not manage any clubs. \
            Answer the following question in his mannerism. 
            """

    user_question = st.text_input("Ask the special one ✨")

    if user_question is not None and user_question != "":
        with st.spinner(text="In progress..."):
            st.write(agent.run(rules + user_question))

if __name__ == "__main__":
    main()