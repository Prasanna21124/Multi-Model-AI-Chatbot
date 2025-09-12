# Multi-Model-AI-Chatbot
An interactive AI chatbot using OpenAI, Google Gemini, and Groq models with support for text, audio, and image inputs built with Streamlit.

## Features
- Chat with multiple AI models (OpenAI GPT-4, Gemini, Groq)
- Upload audio and get transcription + AI response
- Upload images and ask questions about them
- Generate images using DALL-E 3
- Session-based chat history
- Clean UI with selectable input types

## Tech Stack
- Frontend and Framework: Streamlit
- Language: Python
- APIs:<br> OpenAI GPT-4 and Whisper-1<br> Google Gemini<br> Groq LLaMA
- Other tools:<br> Pillow<br> python-dotenv

## Project Structure
Multi-Model-AI-Chatbot/<br>
|-- .env<br>
|-- .gitignore<br>
|-- app.py<br>
|-- README.md 

## Create a Virtual Environment(recommended)<br>
-- python -m venv venv<br>
-- source venv/bin/activate   # On macOS/Linux<br>
-- venv\Scripts\activate # On windows

## Install dependencies
pip install -r requirements.txt

## Set up .env file and store API keys<br>
OPENAI_API_KEY=your_openai_api_key<br>
GEMINI_API_KEY=your_gemini_api_key<br>
GROQ_API_KEY=your_groq_api_key

## Run Streamlit
streamlit run app.py

## Usage Guide
- Choose a Model<br> Select from OpenAI (GPT-4), Gemini, or Groq in the sidebar.
- Choose Input Type<br> Text: Type a question and get an AI response<br> Upload Image: Upload an image and ask about it<br> Upload Audio: Upload audio and get transcribed text<br> Generate Image: Provide a text prompt and generate an image

## Chatbot UI
![Chatbot Screenshot](screenshots/chatbot_ui.png)
