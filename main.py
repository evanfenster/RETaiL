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
import speech_recognition as sr
import pyttsx3
import json

engine = pyttsx3.init()

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
            name = "Query an Attribute of an Item",
            func=worker.query,
            description="used to ask about a specific attribute of an item; input examples: 'price of apples', 'description of eggs', 'quantity of milk', 'precense of bread'",
        ),
    ]

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613", temperature=0.2)
    agent_keyword_args = {"system_message": "Your name is Stocky, and you are an incredibly friendly customer service chatbot for a retail store. After answering, always ask if there is anything else you can help with!"}
    chat = initialize_agent(tools, llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, agent_kwargs=agent_keyword_args, verbose=True, memory=memory)

    return chat

# ------------------------
# SPEECH FUNCTIONS
# ------------------------
def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError as e:
    return False
  return True

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Calibrating...")
        r.adjust_for_ambient_noise(source, duration=5)
        # optional parameters to adjust microphone sensitivity
        r.energy_threshold = 4000
        r.pause_threshold=0.5

        print("Okay, go!")
        while 1:
            text = ""
            print("listening now...")
            audio = r.listen(source, timeout=5, phrase_time_limit=30)
            print("Recognizing...")
            # whisper model options are found here: https://github.com/openai/whisper#available-models-and-languages
            # other speech recognition models are also available.
            
            text = r.recognize_whisper(
                audio,
                model="base.en",
                show_dict=True,
            )["text"]

            print("You said: ")
            print(text)

            
            print("Getting response...")
            # Hacky solution for known langchain issue 
            try:
                response = chat.run(input=text)
            except ValueError as e:
                response = str(e)
                if not response.startswith("Could not parse LLM output:"):
                    unrecognized_speech_text = (f"Sorry, I didn't catch that. Please repeat your question.")
                    print(e)
                    response = unrecognized_speech_text
                else:
                    response = response.removeprefix("Could not parse LLM output: ")
            print(response)
            engine.say(response)
  
            engine.runAndWait()

# ------------------------
# MAIN FUNCTIONS
# ------------------------
def main():
    global chat

    load_dotenv()

    chat = setup_chat()

    listen()
    # question = "How are your cakes?"
    # answer = chat.run(input=question)
    # print(answer)

if __name__ == "__main__":
    main()