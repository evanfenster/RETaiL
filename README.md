# RET\[ai\]L
# Inventory Chatbot

This project contains a Python-based chatbot that interacts with an inventory system. The bot listens to speech input, converts it into text using OpenAI's Whisper ASR system, processes the text to produce an answer, and then speaks the answer back to the user using Text-to-Speech.

## Dependencies

This project uses several Python libraries. Install them using pip:

```bash
pip install -r requirements.txt
```

## How to Run

Execute the script from your terminal:

```bash
python main.py
```

## Configuration

Configure the chatbot with your own OpenAI API key and other necessary details by creating a `.env` file in the project root directory:

```env
OPENAI_API_KEY=your-openai-api-key
```

## Notes

This project is a simple Speech-to-Text chatbot that interacts with an inventory system. It serves as a starting point for creating a more complex and tailored solution. Enjoy using the Inventory Chatbot!