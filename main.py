import os
import time
import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import tempfile
from src.openai_service import story_completion
from dotenv import load_dotenv

load_dotenv()

# Azure Speech service configuration
speech_key = os.getenv("AZURE_SPEECH_KEY")
service_region = os.getenv("AZURE_SPEECH_REGION")

# Check if the environment variables are set
if not speech_key or not service_region:
    st.error("Azure Speech Key and Region must be set in the environment variables.")
else:
    # Global variable to store the transcript
    transcript = ""
    global done  # Global variable to control the recognition loop
    done = False

    def recognize_from_audio_file(audio_file):
        global transcript
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_recognition_language = "zh-HK"  # Correct language code for Cantonese

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            temp_audio_file.write(audio_file)
            temp_audio_file_path = temp_audio_file.name

        audio_input = speechsdk.audio.AudioConfig(filename=temp_audio_file_path)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

        def recognized(evt):
            print("Recognized: {}".format(evt.result.text))  # Print the transcript for logging
            global transcript
            transcript += evt.result.text + " "
            st.session_state.transcript = transcript
            st.write("Recognized: {}".format(evt.result.text))
            print("Recognized: {}".format(evt.result.text))  # Print the transcript for logging

        def stop_cb(evt):
            global done
            print('CLOSING on {}'.format(evt))
            speech_recognizer.stop_continuous_recognition()
            done = True

        speech_recognizer.recognized.connect(lambda evt: recognized(evt))
        speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
        speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
        speech_recognizer.canceled.connect(stop_cb)

        speech_recognizer.start_continuous_recognition_async()

        while not done:
            time.sleep(.5)
            print("Waiting for recognition to finish...")
            print("Transcript: ", transcript)

    st.title("Streamlit Audio Input and STT with Azure")

    audio_file = st.file_uploader("Upload an audio file", type=["wav"])

    if audio_file is not None and not done:
        with st.spinner("Processing audio..."):
            recognize_from_audio_file(audio_file.read())

    # Create an input field
    user_input = st.text_input("Enter your input:", value=transcript, key="user_input",height=200)

    # Display the result in a text area
    if user_input:
        result = story_completion(user_input)
        st.text_area("Result:", value=result, key="result")