from dotenv import load_dotenv
import os
import streamlit as st
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables import RunnableConfig
from agent import chatagent
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables import RunnableConfig
import glob

from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables import RunnableConfig


load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


st.set_page_config(page_title="Algoherence", page_icon="🍮")
st.title("Algoherence Chat")


if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)


avatars = {"human": "user", "ai": "🍮"}
# st.session_state.steps = {}
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
        response = executor.query(prompt, cfg)
        # response = executor.invoke(prompt, cfg)
    
        st.write(response["output"])
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": response["output"]})
        # st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]
    # if not len(os.listdir('./graph')) == 0:
    #     print("Directory is not empty")
    #     print(glob.glob("./graph/*"))
    #     st.image(glob.glob("./graph/*")[0])
    # else:
    #     print("Directory is empty")