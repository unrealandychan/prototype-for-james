import os
import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import tempfile
from src.openai_service import story_completion

# Azure Speech service configuration
speech_key = os.getenv("AZURE_SPEECH_KEY")
service_region = os.getenv("AZURE_SPEECH_REGION")

# Global variable to store the transcript
transcript = ""

def recognize_from_audio_file(audio_file):
    global transcript
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_recognition_language = "zh-HK"  # Correct language code for Cantonese

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        temp_audio_file.write(audio_file)
        temp_audio_file_path = temp_audio_file.name

    audio_input = speechsdk.audio.AudioConfig(filename=temp_audio_file_path)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        transcript = result.text
        st.session_state.transcript = result.text
        st.write("Recognized: {}".format(result.text))
    elif result.reason == speechsdk.ResultReason.NoMatch:
        st.write("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        st.write("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            st.write("Error details: {}".format(cancellation_details.error_details))

st.title("Streamlit Audio Input and STT with Azure")

audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "mp4", "flac"])

if audio_file is not None:
    recognize_from_audio_file(audio_file.read())

# Create an input field
user_input = st.text_input("Enter your input:" ,value=transcript, key="user_input")

# Display the result in the input field
if user_input:
    result = story_completion(user_input)
    st.text_input("Result:", value=result, key="result")