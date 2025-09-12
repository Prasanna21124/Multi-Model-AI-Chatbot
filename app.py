from openai import OpenAI
from google import genai  
from groq import Groq  
import streamlit as st
from dotenv import load_dotenv
import base64
import os
import io
from PIL import Image
from google.genai import types

# Function to display chat history for specified model
def display_chat(chat_history, model_name):
    st.subheader("**Output:**")
    for chat in chat_history:
        if chat["role"] == "user":
            st.markdown(f"**You:** {chat['content']}")
        else:
            if "image_url" in chat['content']:
                st.image(chat["content"]["image_url"], caption=f"{model_name} Output")
            else:
                st.markdown(f"**{model_name}:** {chat['content']}")
# Load API keys
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
gemini_api_key = os.getenv('GEMINI_API_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')

# Initialize clients 
openai_client = OpenAI(api_key=openai_api_key)
gemini_client = genai.Client(api_key = gemini_api_key)
groq_client = Groq(api_key=groq_api_key)

# Streamlit setup
st.title("Multi-Model AI Chatbot")

# Initialize session chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar model selector
model_choice = st.sidebar.selectbox(
    "Choose Model",
    ["OpenAI (GPT-4)", "Gemini", "Groq"]
)

input_type = st.selectbox(
    "Choose input type:",
    ["Text", "Upload Image", "Upload Audio", "Generate Image"]
)
# Initialize input variables
user_input = ""
uploaded_image = None
uploaded_audio = None
user_input_img = ""

# Input field based on selection
if input_type == "Text":
    user_input = st.text_input("Type your question:")

elif input_type == "Upload Image":
    uploaded_image = st.file_uploader("Upload an image (jpg, png):", type=["jpg", "jpeg", "png"])
    user_input = st.text_input("Question about the image: ")

elif input_type == "Upload Audio":
    uploaded_audio = st.file_uploader("Upload an audio (mp3, wav, m4a):", type=["mp3", "wav", "m4a"])

elif input_type == "Generate Image":
    user_input_img = st.text_input("Enter prompt for image generation: ")

if st.button("Ask"):
    if not user_input.strip() and not user_input_img.strip() and uploaded_image is None and uploaded_audio is None:
        st.warning("Please enter something!")
    else:
        try:
            #OPENAI
            if model_choice == "OpenAI (GPT-4)":
                # Voice transcription
                if uploaded_audio is not None:
                    with st.spinner("Transcribing audio..."):
                        audio_bytes = uploaded_audio.read()
                        audio_file = io.BytesIO(audio_bytes)
                        audio_file.name = uploaded_audio.name  
                        response = openai_client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file
                        )
                        transcribed_text = response.text
                        st.session_state.chat_history.append({"role": "assistant", "content": transcribed_text})

                        response = openai_client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=st.session_state.chat_history
                        )
                        answer = response.choices[0].message.content
                        display_chat(st.session_state.chat_history, model_choice)
            
                # Image generation
                elif user_input_img.strip():
                    with st.spinner("Generating image..."):
                        st.session_state.chat_history.append({"role": "user", "content": user_input_img})
                        response = openai_client.images.generate(
                            model="dall-e-3",
                            prompt=user_input_img,
                            size="1024x1024",
                            n=1
                        )
                        image_url = response.data[0].url
                        answer = f"Generated image for: "
                        st.session_state.chat_history.append({"role": "assistant", "content": {"type": "image", "image_url": image_url, "description": f"Generated image for: {user_input_img}"}})

                        display_chat(st.session_state.chat_history, model_choice)

                # Image Q&A
                elif uploaded_image is not None:
                    with st.spinner("Analyzing image..."):
                        st.session_state.chat_history.append({"role": "user", "content": user_input})
                        image_bytes = uploaded_image.read()
                        base64_image = base64.b64encode(image_bytes).decode("utf-8")
                        response = openai_client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "user", "content": [
                                    {"type": "text", "text": user_input},
                                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                                ]}
                            ],
                        )
                        answer = response.choices[0].message.content
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})

                        display_chat(st.session_state.chat_history, model_choice)


                # Normal text chat
                else:
                    if user_input.strip() is not None:
                        with st.spinner("Thinking..."):
                            st.session_state.chat_history.append({"role": "user", "content": user_input})
                            response = openai_client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=st.session_state.chat_history
                            )
                            answer = response.choices[0].message.content
                            st.session_state.chat_history.append({"role": "assistant", "content": answer})

                            display_chat(st.session_state.chat_history, model_choice)

            #GEMINI
            elif model_choice == "Gemini":
                with st.spinner("Thinking..."):
                    if user_input_img.strip() or uploaded_audio is not None:
                        raise Exception("Gemini does not support audio input. Please provide text or an image.")
                    elif uploaded_image:
                        st.session_state.chat_history.append({"role": "user", "content": user_input})
                        image_bytes = uploaded_image.read()  

                        response = gemini_client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[
                                types.Part.from_bytes(
                                    data=image_bytes,
                                    mime_type='image/jpeg'  
                                ),
                                user_input if user_input else "Caption this image."
                            ]
                        )

                        answer = response.text
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    elif user_input.strip(): 
                        with st.spinner("Thinking..."):
                            st.session_state.chat_history.append({"role": "user", "content": user_input})
                            response = gemini_client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=user_input
                            )

                            answer = response.text
                            st.session_state.chat_history.append({"role": "assistant", "content": answer})

                    display_chat(st.session_state.chat_history, model_choice)

            #GROQ
            elif model_choice == "Groq":
                with st.spinner("Thinking..."):
                    if user_input_img.strip() or uploaded_audio is not None or uploaded_image is not None:
                        raise Exception("Groq does not support audio and image input. Please provide text only.")
                    
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    messages = st.session_state.chat_history
                    response = groq_client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=messages
                    )
                    answer = response.choices[0].message.content
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})

                    display_chat(st.session_state.chat_history, model_choice)

        except Exception as e:
            st.error(f"Something went wrong: {(e)}")
