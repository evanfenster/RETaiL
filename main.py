import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent
from langchain.agents import Tool
from langchain.agents import AgentType
from typing import Optional
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
import sqlite3
import pandas as pd
import streamlit as st
import random
import schedule
import time

engine = pyttsx3.init()

global chat, cursor, connection
global inventory_updates 

# ------------------------
# SETUP FUNCTIONS
# ------------------------
def setup_chat() -> Optional[ChatOpenAI]:
    """Setup the chatbot. This function is called when the chatbot is first initialized."""
    worker = inventory_worker
    worker.main()

    tools = [
        Tool(
            name = "Query an Attribute of a Grocery Store Item",
            func=worker.query,
            description="used to ask about a specific attribute of an item; input examples: 'price of apples', 'description of eggs', 'quantity of milk', 'asile of bread'",
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

# Function to create connection with SQLite database
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

# Function to execute a query and return the results as a DataFrame
def execute_query(conn, query):
    df = pd.read_sql_query(query, conn)
    return df

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def chat_ui():
    global inventory_updates
    # Call the local_css function and pass the name of your css file.
    local_css("style.css")

    # Function to display data from the SQLite database
    def display_data():
        database = "inventory.db"
        table_name = "Inventory"

        conn = create_connection(database)

        query = f"SELECT * FROM {table_name}"
        df = execute_query(conn, query)
        
        st.dataframe(df)
    display_data()  # Call the function to display data
    
    
    st.sidebar.markdown(
        """
        ## Stocky 🛒
        Stocky is your shopping assistant. Start a conversation in the chat box and Stocky will respond to your shopping needs! \n
        Stocky can dynamically query the store's database and answer questions about the store's inventory.
        Feel free to ask about:
        - price
        - quantity
        - description
        - aisle \n
        of any item in the store.
        \n \n
        Happy shopping! 🛍️
        \n
        """
    )

    st.sidebar.markdown("### Inventory Updates")
    for update in inventory_updates:
        st.sidebar.write(update)

    st.title("Chat with Stocky! 🛒")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Hey, I'm Stocky! I'm here to help you with your shopping needs. How can I help you today?"}]

    for msg in st.session_state.messages:  # Exclude the last message which is potentially still loading
        if msg["role"] == "assistant":
            st.chat_message("🤖").write(msg["content"])
        else:
            st.chat_message("👤").write(msg["content"])

    prompt = st.chat_input()

    if prompt:
        update = simulate_shopper_buy()
        inventory_updates.append(update)
        st.sidebar.markdown("📢 Inventory Update 📢")
        st.sidebar.write(update)

        # input validation to prevent empty messages
        if prompt.strip() == '':
            st.warning("Message cannot be empty.")
            return

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("👤").write(prompt)

        with st.spinner("Stocky is typing..."):
            try:
                # Get assistant's response
                response = chat.run(input=prompt)

                # Update assistant's response
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {str(e)}")

        # Force a rerun to reflect updated response
        st.experimental_rerun()

    if st.button("Clear chat"):
        st.session_state.messages = []

# ------------------------
# SIMULATION FUNCTIONS
# ------------------------
def get_items() -> list:
    """Get all items in the database and return them as a list."""
    cursor.execute("SELECT ProductName FROM Inventory")
    items = cursor.fetchall()
    return [item[0] for item in items]

# def simulate_shopper(interval):
#     # Start a new thread, passing the database path to it
#     schedule.every(interval).seconds.do(simulate_shopper_thread)

def simulate_shopper_buy():
    global connection, cursor, inventory_updates
    # Get a random item from the list of items
    items = get_items()
    if items:
        item = random.choice(list(items))
        # Get the current quantity of the item
        cursor.execute("SELECT QuantityInStock FROM Inventory WHERE ProductName = ?", (item,))
        quantity = cursor.fetchone()[0]
        # If the item is in stock, subtract one and update the database
        if quantity > 0:
            quantity -= 1
            cursor.execute("UPDATE Inventory SET QuantityInStock = ? WHERE ProductName = ?", (quantity, item))
            connection.commit()  # commit the changes to the database
            update_message = f"A shopper has bought a {item}. There are now {quantity} left in stock."
            print(update_message)
            print(len(inventory_updates))
        else:
            update_message = f"There are no more {item} left in stock."
            print(update_message)
    
    return update_message
    


# ------------------------
# MAIN FUNCTIONS
# ------------------------
def main():
    global chat, connection, cursor, inventory_updates

    load_dotenv()

    # Initialize "inventory_updates" key with an empty list
    inventory_updates = []

    # Connect to the SQLite database
    connection = sqlite3.connect('inventory.db')
    cursor = connection.cursor()

    chat = setup_chat()

    listen()
    #chat_ui()

if __name__ == "__main__":
    main()