import pyautogui as pya
import pyperclip
from openaiclient import get_completion, get_image_completion
from image_process import capture_active_window


# This is the main list of functions that can be called by the AI. Create a new function then describe it here.
functions = [
    {
        "name": "process_text",
        "description": "Process text in a user defined way by sending it to the openai api",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "the prompt to send to the openai api. This is what the user wants to do with the text. Do not include the text, just determine the prompt by analyzing the intent.",
                },
            },
            "required": ["prompt"],

            },
        },

    {
        "name": "process_screen",
        "description": "Process the screen by taking a screen shot and sending it to the OpenAI vision api.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "the prompt to send to the openai vision api. This is what the user wants to do with the image. Determine the prompt by analyzing the users intent. for example they might say 'tell me what im looking at' or 'what color is the sky' or 'what is the name of this app on the screen'",
                },
            },
            "required": ["prompt"],

            },
        },
]

#####################
# Function calls
#####################

def process_text(prompt):
  """
  Process the given text prompt and return a response object.
  
  Args:
      prompt (str): The text prompt to process.
  
  Returns:
      dict: A response object containing the name of the function called and the response.
  """
  print("processing text with prompt: " + prompt)

  #get the text from the clipboard
  text = pyperclip.paste()

  #send the text to the openai api
  new_text = get_completion(prompt + "\n" + text)

  #create a response object, include the name of the function called and the response
  response = {"function_called": "process_text", "response": new_text}
  
  #return the response object
  return response


def process_screen(prompt):
    """
    Process the screen with the given prompt.

    Parameters:
    - prompt (str): The prompt to be used for image completion.

    Returns:
    - response (dict): A dictionary containing the name of the function called and the response.
    """
    print("processing screen with prompt: " + prompt)
    base64_image = capture_active_window("output.png")

    #send the image to the openai api
    new_text = get_image_completion(base64_image, prompt)

    print(new_text)

    #create a response object, include the name of the function called and the response
    response = {"function_called": "process_screen", "response": new_text}
    
    #return the response object
    return response
            

            