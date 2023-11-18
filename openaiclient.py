from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
from prompts import image_description

load_dotenv()
client = OpenAI()

#TODO: Convert this to a class


def get_completion(prompt, model="gpt-3.5-turbo"):
  """
  Generates a completion for a given prompt using the given model.

  :param prompt: The prompt for which to generate a completion.
  :param model: The model to use for generating the completion. Default is "gpt-3.5-turbo".
  :return: The generated completion as a string.
  """

  messages = [{"role": "assistant", "content": "you are a helpful assistant"}]
  messages.append({"role": "user", "content": prompt})
  
  response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=300,
                )
  assistant_response = response.choices[0].message.content

  #clear messages
  messages = []

  return assistant_response



def get_image_completion(base64_image, prompt = image_description, model="gpt-4-vision-preview"):
    """
    This function takes in a base64 encoded image and a prompt, and uses the OpenAI API to generate a description of the image or process it accoring to the users prompt.

    Parameters:
        - base64_image (str): The base64 encoded image.
        - prompt (str, optional): The prompt to use for image description. Defaults to image_description.
        - model (str, optional): The model to use for image completion. Defaults to "gpt-4-vision-preview".

    Returns:
        - description (str): The generated description of the image.

    Raises:
        - Exception: If an error occurs during the API call.
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            "max_tokens": 300,
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        
        description = (
            response.json()
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        
        return description
    except Exception as e:
        return str(e)
