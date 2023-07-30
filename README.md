# Stocky: A Customer Service Chatbot for Retail Stores

Stocky is an intelligent and responsive customer service chatbot tailored for retail stores. Utilizing speech recognition and natural language understanding, Stocky can dynamically query a store's database to answer questions about inventory, simulate shopper behaviors, and interact with customers both through voice and a text-based UI.

## Features

- **Query Inventory Information**: Ask about price, quantity, description, and aisle of any item in the store.
- **Voice Interactions**: Communicate with Stocky through voice using `speech_recognition` and `pyttsx3` libraries.
- **Simulate Shopping Behavior**: Simulate a shopper buying items with real-time inventory updates.
- **Friendly Text-based UI**: Engage with Stocky using an intuitive chat interface built with Streamlit.

## Installation

1. **Clone the Repository**: Clone this repository to your local machine.

2. **Set Up a Virtual Environment**: It is recommended to use a virtual environment to manage dependencies.

3. **Install Dependencies**: Install the required packages using pip and the provided `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

4. **Database Configuration**: Make sure the `inventory.db` SQLite database is in the root directory with the required schema.

5. **Environment Variables**: If required, place a `.env` file in the root directory with necessary API keys or other environment-specific variables.

## Usage

1. **Start the Chatbot**:

   ```bash
   python main.py
   ```

2. **Chat Interface**: Open the provided link to interact with Stocky through the Streamlit interface.

3. **Voice Interaction**: Uncomment the `listen()` line in the `main()` function if you wish to enable voice interaction.

4. **Customization**: Modify the tools, prompts, or other functionalities to suit your specific needs.

## Example Queries

You can ask Stocky questions like:

- "What is the price of apples?"
- "How many loaves of bread are left?"
- "Where can I find eggs?"