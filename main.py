
from dotenv import load_dotenv

load_dotenv()
import io
import json
from typing import Annotated
from pptx import Presentation
from openai import OpenAI
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
import os
from PIL import Image

import pyaudio
import requests
import typer
from pine import search_pipeline, index_folder, delete_all_documents
from RealtimeSTT import AudioToTextRecorder
from function_calls import functions, process_text, process_screen
import soundfile as sf
import sounddevice as sd

import pyperclip
import pyautogui
from prompts import coding_prompt,assistant_prompt
from rich import print


app = typer.Typer()
client = OpenAI()



@app.command(name="index")
def index(folder_path="files"):
    index_folder()
    print("Indexing complete.")


@app.command(name="delete")
def delete():
    delete_all_documents()


def handle_function_call(data):
    """
    Asynchronously handles a function call by evaluating the specified function with the given arguments.

    Args:
        data: The data object containing the function call information.

    Returns:
        The result of the evaluated function call.

    Raises:
        Any exceptions that may occur during the evaluation of the function call.
    """
    function_name = data.message.function_call.name
    arguments = json.loads(data.message.function_call.arguments)
    return eval(function_name)(**arguments)



def stream_audio(input_text, model='tts-1', voice='alloy'):
    """
    Generates a function comment for the given function body.
    
    Args:
        input_text (str): The input text to be converted to audio.
        model (str, optional): The model to be used for audio generation. Defaults to 'tts-1'.
        voice (str, optional): The voice to be used for audio generation. Defaults to 'alloy'.
    
    Returns:
        None
    """
   
    # OpenAI API endpoint and parameters
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f'Bearer {os.environ["OPENAI_API_KEY"]}',
    }

    data = {
        "model": model,
        "input": input_text,
        "voice": voice,
        "response_format": "opus",
    }

    audio = pyaudio.PyAudio()

    def get_pyaudio_format(subtype):
        if subtype == 'PCM_16':
            return pyaudio.paInt16
        return pyaudio.paInt16

    with requests.post(url, headers=headers, json=data, stream=True) as response:
        if response.status_code == 200:
            buffer = io.BytesIO()
            for chunk in response.iter_content(chunk_size=4096):
                buffer.write(chunk)
            
            buffer.seek(0)

            with sf.SoundFile(buffer, 'r') as sound_file:
                format = get_pyaudio_format(sound_file.subtype)
                channels = sound_file.channels
                rate = sound_file.samplerate

                stream = audio.open(format=format, channels=channels, rate=rate, output=True)
                chunk_size = 1024
                data = sound_file.read(chunk_size, dtype='int16')
                

                while len(data) > 0:
                    stream.write(data.tobytes())
                    data = sound_file.read(chunk_size, dtype='int16')

                stream.stop_stream()
                stream.close()
        else:
            print(f"Error: {response.status_code} - {response.text}")

        audio.terminate()

# Chat mode that loops and asks for input, sends to openai
@app.command(name="chat")
def chat(
    voice: bool = typer.Option(False, "--voice"), 
    auto_enter: bool = typer.Option(False, "--auto_enter"), 
    mute: bool = typer.Option(False, "--mute"),
    coding_mode: bool = typer.Option(False, "--coding_mode"),
):
    """
    Runs a chat application that interacts with an AI model.
    
    Args:
        voice (bool, optional): Whether to enable voice input/output. Defaults to False.
        auto_enter (bool, optional): Whether to automatically press enter after each dictation. Defaults to False.
        mute (bool, optional): Whether to mute the chat microphone. Defaults to False.
        coding_mode (bool, optional): Whether to enable coding mode. Defaults to False.
    
    Returns:
        None
    """
    print("""_____              _____    _   _   ______   _        _        
 |  __ \     /\     |  __ \  | \ | | |  ____| | |      | |       
 | |  | |   /  \    | |__) | |  \| | | |__    | |      | |       
 | |  | |  / /\ \   |  _  /  | . ` | |  __|   | |      | |       
 | |__| | / ____ \ _| | \ \ _| |\  |_| |____ _| |____ _| |____ _ 
 |_____(_)_/    \_(_)_|  \_(_)_| \_(_)______(_)______(_)______(_)
""")
    mode = "AI"  # Starting in AI mode
    muted = mute 

    with AudioToTextRecorder() as recorder:
        messages = [{
            "role": "system",
            "content": assistant_prompt,
        }]
        # Dictionary of commands and their actions
        commands = {
            'exit.': 'break',
            'mute.': 'mute',
            'mute': 'mute',
            'mew': 'mute',
            'mew.': 'mute',
            'unmute': 'unmute',
            'dictate': 'dictate',
            'dictate mode': 'dictate',
            'dictate mode.': 'dictate',
            'dictation mode': 'dictate',
            'dictation mode.': 'dictate',
            'coding mode': 'coding',
            'coding mode.': 'coding',
            'a.i.' : 'ai',
            'a.i': 'ai',
            'ai': 'ai',
            'ai.': 'ai',
            'a.i. mode': 'ai',
            'a.i. mode': 'ai',
            'a.i. mode.': 'ai',
            
        }
        # Loop until 'break' is entered
        while True:
            if not muted:
                #print the current mode
                print("Current mode:", mode)
                
                user_input = recorder.text().strip()
            else:
                user_input = typer.prompt("Type input").strip()

            if not user_input:
                continue

            command_action = commands.get(user_input.lower())

            if command_action == 'break':
                break
            elif command_action == 'mute':
                muted = True
                print("Muted")
                continue
            elif command_action == 'unmute':
                muted = False
                print("Unmuted")
                continue
            elif command_action == 'dictate':
                mode = "Dictate"
                continue
            elif command_action == 'coding':
                mode = "Coding"
                continue
            elif command_action == 'ai':
                mode = "AI"
                continue

            if mode == "AI":
                print(f"You: {user_input}")
                messages.append({"role": "user", "content": user_input})

                response = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=messages,
                    max_tokens=300,
                    functions=functions,
                )
                assistant_response = response.choices[0].message.content
                if response.choices[0].finish_reason == "function_call":
                    ai_response = handle_function_call(response.choices[0])

                    #can process the returns of different functions in funccalls.py here
                    if ai_response["function_called"] == "process_text":
                        pyperclip.copy(ai_response["response"])
                        pyautogui.hotkey('ctrl', 'v')
                        pyautogui.press('enter')
                        messages.append({"role": "assistant", "content": ai_response["response"]})

                    elif ai_response["function_called"] == "process_screen":
                        pyperclip.copy(ai_response["response"])
                        #if voice:
                        #  stream_audio(ai_response["response"])
                        messages.append({"role": "assistant", "content": ai_response["response"]})
                        
                else:
                    print(assistant_response)
                    if voice:
                        stream_audio(assistant_response)
                        messages.append({"role": "assistant", "content": assistant_response})
            elif coding_mode or mode == "Coding":  # Handle Coding Mode
                messages = [
                    {"role": "system", "content": coding_prompt},
                    {"role": "user", "content": user_input}
                ]
                response = client.chat.completions(
                    model="gpt-4-1106-preview",
                    messages=messages,
                    max_tokens=1200
                )
                assistant_response = response['choices'][0]['message']['content']
                code_response = assistant_response.strip()
                #type the
                pyautogui.typewrite(code_response)
            # Handle Dictation Mode   
            elif mode == "Dictate":
                pyautogui.typewrite(user_input)
                pyautogui.press('enter' if auto_enter else 'space')
                  

if __name__ == "__main__":

    app()
