
from flask import Flask, request, jsonify
import os
import logging
from openai import AzureOpenAI
app = Flask(__name__)
# Configure logging
logging.basicConfig(level=logging.INFO)
# Environment variables
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
MODEL_NAME = os.getenv("MODEL_NAME")  # Model name as a Docker env variable
MAX_TOKENS = os.getenv("MAX-TOKENS")
def ask_gpt_problem(prompt_system, prompt_user, json_format_output, temperture = 0):
    messages = [
        {"role": "system", "content": prompt_system},
        {"role": "user", "content": prompt_user}
    ]
    
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT, 
        api_key=AZURE_OPENAI_API_KEY,  
        api_version=AZURE_OPENAI_API_VERSION
    )
    
    if json_format_output:
        logging.info("JSON format activated")
        chat_response = client.chat.completions.create(
            model=MODEL_NAME,
            response_format={"type": "json_object"},
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=temperture
        )       
    else:
        chat_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=temperture
        )
    
    logging.info(f'This is the chat response \n {chat_response.choices[0].message.content}')
    # Extract the content from the response
    message_content = chat_response.choices[0].message.content
    return message_content
@app.route('/v1/ask_gpt', methods=['POST'])
def ask_gpt():
    data = request.get_json()
    prompt_system = data.get('prompt_system', '')
    prompt_user = data.get('prompt_user', '')
    json_format_output = data.get('json_format_output', True)
    temperature = data.get('temperture', 0)
    
    logging.info('Received new request')
    response = ask_gpt_problem(
        prompt_system=prompt_system,
        prompt_user=prompt_user,
        json_format_output=json_format_output
    )
    return jsonify({'response': response})
if __name__ == '__main__':
    # For Cloud Run, listen on all IPs and port 8080
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
