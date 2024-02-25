import cohere
from dotenv import load_dotenv
import os
from pathlib import Path
import streamlit as st
from langchain import hub
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain_community.callbacks import StreamlitCallbackHandler
# from langchain_community.utilities import DuckDuckGoSearchAPIWrapper, SQLDatabase
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables import RunnableConfig
from sqlalchemy import create_engine
from agent import chatagent


load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

from langchain.agents import ConversationalChatAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
# from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

import streamlit as st

st.set_page_config(page_title="Algoherence", page_icon="🍮")
st.title("Algoherence Chat")

msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)

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

    # llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai_api_key, streaming=True)
    # tools = [DuckDuckGoSearchRun(name="Search")]
    # chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools)
    # executor = AgentExecutor.from_agent_and_tools(
    #     agent=chat_agent,
    #     tools=tools,
    #     memory=memory,
    #     return_intermediate_steps=True,
    #     handle_parsing_errors=True,
    # )
    executor  = chatagent()

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        cfg = RunnableConfig()
        cfg["callbacks"] = [st_cb]
        # response = executor.invoke(prompt, cfg)
        response = executor.query(prompt, cfg)
        st.write(response["output"])
        # st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]