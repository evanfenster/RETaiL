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
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

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
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613", temperature=0)
    agent_keyword_args = {"system_message": "You are an incredibly friendly chatbot. Always add a ':)' to the end of your messages."}
    chat = initialize_agent(tools, llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, agent_kwargs=agent_keyword_args, verbose=True, memory=memory)

    return chat

# ------------------------
# MAIN FUNCTIONS
# ------------------------

def main():
    global chain

    load_dotenv()

    chat = setup_chat()
    question = "Do you have cake?"
    answer = chat.run(input=question)
    print(answer)

if __name__ == "__main__":
    main()