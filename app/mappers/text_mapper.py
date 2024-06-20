import json
import requests

def extract_text_from_response(response: requests.Response) -> str:
    try:
        data = response.json()
        text = data['result']['alternatives'][0]['message']['text']
        return text
    except (KeyError, IndexError, json.JSONDecodeError):
        return "Извините, произошла ошибка при обработке ответа."