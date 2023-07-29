import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent
from langchain.agents import Tool
from langchain.agents import AgentType
from typing import Optional
from pydantic import BaseModel, Field
from langchain.chat_models import ChatOpenAI
import worker as inventory_worker

global chat

# ------------------------
# CHAT FUNCTIONS
# ------------------------
def setup_chat() -> Optional[ChatOpenAI]:
    """Setup the chatbot. This function is called when the chatbot is first initialized."""
    worker = inventory_worker
    worker.main()

    tools = [
        Tool(
            name = "Query",
            func=worker.query,
            description="used to find info about a product; returns 'NA' if the item is not in the store",
        ),
    ]

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    llm = ChatOpenAI(temperature=0)
    chat = initialize_agent(tools, llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory)

    return chat

# ------------------------
# MAIN FUNCTIONS
# ------------------------

def main():
    global chain

    load_dotenv()

    chat = setup_chat()
    question = "Do you have cake?"
    answer = chat.run(question)
    print(answer)

if __name__ == "__main__":
    main()