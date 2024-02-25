from dotenv import load_dotenv
import os
import streamlit as st
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnableConfig
from agent import chatagent
import pandas as pd
import numpy as np
import glob
import warnings
warnings.filterwarnings("ignore")

load_dotenv()


st.set_page_config(page_title="Algoherence", page_icon="🍮")
st.title("Algoherence Chat")

msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)

if len(msgs.messages) == 0:
    msgs.clear()
    msgs.add_ai_message("How can I help you?")
    st.session_state.steps = {}

avatars = {"human": "user", "ai": "🍮"}
for idx, msg in enumerate(msgs.messages):
    with st.chat_message(avatars[msg.type]):
        # Render intermediate steps if any were saved
        for step in st.session_state.steps.get(str(idx), []):
            if step[0].tool == "_Exception":
                continue
            with st.status(f"**{step[0].tool}**: {step[0].tool_input}", state="complete"):
                st.write(step[0].log)
                st.write(step[1])
        st.write(msg.content)

if prompt := st.chat_input(placeholder="Can you run the mean reversion algorithm on 10 shares MSFT?"):
    st.chat_message("user").write(prompt)

    executor  = chatagent()

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        cfg = RunnableConfig()
        cfg["callbacks"] = [st_cb]
        response = executor.query(prompt, cfg, memory)
        st.write(response["output"])
        st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]
        if os.path.isdir('./graph'):
            if not len(os.listdir('./graph')) == 0:
                print("Graph directory is not empty")
                image_file_path = glob.glob("./graph/*")[0]
                st.image(glob.glob(image_file_path))
                os.remove(image_file_path)
            else:
                print("Graph directory is empty")
        if os.path.isdir('./table'):
            if not len(os.listdir('./table')) == 0:
                print("Table directory is not empty")
                csv_file_path = glob.glob("./table/*")[0]
                df = pd.read_csv(csv_file_path)
                st.dataframe(df)
                os.remove(csv_file_path)
            else:
                print("Table directory is empty")