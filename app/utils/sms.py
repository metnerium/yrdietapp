import secrets
import string
import requests

def get_auth_code():
    return ''.join(secrets.choice(string.digits) for _ in range(4))

def send_sms(phone_number, code):
    url = f'http://api.smsfeedback.ru/messages/v2/send?login=metnerium&password=Fogot173546&phone={phone_number}&text=Код авторизации - {code}'
    response = requests.get(url)
    return response.status_code == 200
