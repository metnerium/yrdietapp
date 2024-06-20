import requests
import os
from config import SECRET_API_KEY
from config import ID_KEY

url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
api_key = SECRET_API_KEY
sa_id = ID_KEY

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Api-Key {api_key}'
}

def send_diet(message: str) -> requests.Response:
    data = {
        "modelUri": f"gpt://{sa_id}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": "1000"
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты персональный диетолог, отвечай на все вопросы как лучший специалист, отвечай по существу, без воды"
            },
            {
                "role": "user",
                "text": message
            }
        ]
    }

    response = requests.post(url, json=data, headers=headers)
    return response
def send_post(message: str) -> requests.Response:
    data = {
        "modelUri": f"gpt://{sa_id}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": "1000"
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты — опытный копирайтер. Напиши текст с учётом вида текста и заданной темы."
            },
            {
                "role": "user",
                "text": message
            }
        ]
    }

    response = requests.post(url, json=data, headers=headers)
    return response