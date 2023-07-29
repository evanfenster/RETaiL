from typing import Optional
from langchain.chains.openai_functions import (
    create_openai_fn_chain,
    create_structured_output_chain,
)
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import sqlite3

global cursor, chain

# ------------------------
# DATABASE FUNCTIONS
# ------------------------
def get_id(item: str) -> int:
    """Get the ProductID of an item. 

    Args:
        item: The item to get the ProductID of.
    """

    cursor.execute("SELECT ProductID FROM Inventory WHERE ProductName = ?", (item,))
    id = cursor.fetchone()
    if id:
        return id[0]
    else:
        return None

def get_quantity(item: str) -> int:
    """Get the quantity of an item in stock from its ID. The first letter should be capitalized, and the item should not be pluralized.

    Args:
        item: The item to get the quantity of.
    """

    id = get_id(item)

    cursor.execute("SELECT QuantityInStock FROM Inventory WHERE ProductID = ?", (id,))
    quantity = cursor.fetchone()
    if quantity:
        return quantity[0]
    else:
        return None

def get_price(item: str) -> int:
    """Get the price of an item from its ID. The first letter should be capitalized, and the item should not be pluralized.

    Args:
        item: The item to get the price of.
    """

    id = get_id(item)

    cursor.execute("SELECT Price FROM Inventory WHERE ProductID = ?", (id,))
    price = cursor.fetchone()
    if price:
        return price[0]
    else:
        return None

# ------------------------
# CHAT FUNCTIONS
# ------------------------
def setup_chat() -> Optional[ChatOpenAI]:
    # If we pass in a model explicitly, we need to make sure it supports the OpenAI function-calling API.
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    prompt_msgs = [
        SystemMessage(
            content="You are a world class algorithm for extracting information in structured formats."
        ),
        HumanMessage(
            content="Use the given format to extract information from the following input:"
        ),
        HumanMessagePromptTemplate.from_template("{input}"),
        HumanMessage(content="Tips: Make sure to answer in the correct format"),
    ]
    prompt = ChatPromptTemplate(messages=prompt_msgs)

    chain = create_openai_fn_chain([get_quantity, get_price], llm, prompt, verbose=True)
    return chain


# ------------------------
# MAIN FUNCTION
# ------------------------
# Create our main function
def main():
    global cursor, chain
    load_dotenv()

    # Connect to the SQLite database
    connection = sqlite3.connect('inventory.db')
    cursor = connection.cursor()
    
    # Get our LLM chain
    chain = setup_chat()
    question = "I really need some apples. How many apples do you have in stock?"
    details = chain.run(question)
    print(details)
    
    # Answer is in the format {"name": "<<function_name>>", "arguments": {<<function_arguments>>}}
    # We can use this to call the function and get the answer
    # Call the function 
    func_name = details["name"]
    args = details["arguments"]
    func = globals()[func_name]
    result = func(**args)

    # Print the result
    print(result)

    # Close the connection to the database
    connection.close()

if __name__ == "__main__":
    main()