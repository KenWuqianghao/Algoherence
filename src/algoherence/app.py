import streamlit as st
import os
import glob
import pandas as pd
from algoherence.agent import TradingAgent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

st.set_page_config(
    page_title="Algoherence | Smart Trading Assistant",
    page_icon="💹",
    layout="wide"
)

# Custom CSS for a more modern look
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stChatMessage {
        border-radius: 15px;
        margin-bottom: 10px;
    }
    .stChatInput {
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("💹 Algoherence")
st.subheader("Your AI-powered companion for financial literacy and trading.")

# Initialize Agent
if "agent" not in st.session_state:
    try:
        st.session_state.agent = TradingAgent()
    except Exception as e:
        st.error(f"Failed to initialize Trading Agent: {e}")
        st.info("Please ensure COHERE_API_KEY is set in your environment.")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Sidebar for extra features or settings
with st.sidebar:
    st.title("Dashboard")
    st.write("Current Strategy: Mean Reversion")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.write("### Latest Reports")
    tables = glob.glob("table/*.csv")
    if tables:
        selected_table = st.selectbox("View Backtest Results", tables)
        if selected_table:
            df = pd.read_csv(selected_table)
            st.dataframe(df.head(10))
    else:
        st.info("No backtests performed yet.")

# Display Chat Messages
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user", avatar="👤"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(message.content)
    elif isinstance(message, ToolMessage):
        # Optionally show tool outputs in a collapsed section
        with st.expander(f"Tool Result: {message.name if hasattr(message, 'name') else 'Execution'}"):
            st.code(message.content)

# Chat Input
if prompt := st.chat_input("How can I help you today? (e.g., 'Analyze MSFT' or 'Buy 10 shares of AAPL')"):
    # Add human message to chat
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate Agent Response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            # Get only message history for context (Human/AI messages only)
            # LangGraph handles its own internal state, but we can pass history
            result = st.session_state.agent.query(prompt, chat_history=st.session_state.messages[:-1])

            # Extract new messages from the result state
            new_messages = result["messages"][len(st.session_state.messages):]

            # Display results
            for msg in new_messages:
                st.session_state.messages.append(msg)
                if isinstance(msg, AIMessage) and msg.content:
                    st.markdown(msg.content)
                elif isinstance(msg, ToolMessage):
                    with st.expander("Tool Output"):
                        st.code(msg.content)

            # Handle potential artifacts (graphs)
            graphs = glob.glob("graph/*.png")
            if graphs:
                for graph_path in graphs:
                    st.image(graph_path)
                    # Optionally remove after displaying or keep them for the session
                    os.remove(graph_path)

            # Handle potential artifacts (tables)
            tables = glob.glob("table/*.csv")
            if tables:
                # We show the most recent one if it was just created
                # In a more complex app, we might want to link it specifically to the tool call
                pass
