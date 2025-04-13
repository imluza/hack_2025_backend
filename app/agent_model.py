import requests
import json
import os
from dotenv import load_dotenv

def analyze_title(title, description):
    load_dotenv()
    OLLAMA_URL = os.getenv("OLLAMA_URL")
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "python-requests/2.31.0"
    }

    payload = {
        "model": "llama3.1",
        "prompt": f"""
    Проанализируй цель краудфандинговой кампании. Для каждой цели укажи:

    valid: true, если цель этичная и положительная, false — если цель сомнительная или неэтичная, doubt — если цель вызывает сомнения и требует дополнительного анализа.

    reason: Объяснение, почему цель считается этичной или нет.

    e: Оценка проекта от 1 до 5 в сфере экологии.
    g: Оценка проекта от 1 до 5 в сфере корпоративного управления.
    s: Оценка проекта от 1 до 5 в сфере социаального взаимодействия.


    Ответ должен быть в виде списка объектов JSON с полями id, valid, reason, e, g и s. Не должно быть другого текста.

    Пример ответа:
    [
        {{ "id": 1, "valid": "false", "reason": "Преследует личные цели: покупка автомобиля", "e" :"1",  "g":"1", s:"1"}},
        {{ "id": 2, "valid": "true", "reason": "Благотворительность: постройка детского дома","e" :"4",  "5":"1", s:"5" }}
    ]

    Вот цель:
    {title} - {description}
    """,
        "temperature": 0.0,
        "top_p": 0.9,
        "top_k": 20,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5,
        "stream": False,
        "json_mode": True
    }

    response = requests.post(
        OLLAMA_URL,
        headers=headers,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8")
    )

    if response.status_code == 200:
        try:
            json_response = response.json()

            if isinstance(json_response, dict) and 'response' in json_response:
                raw_response = json_response['response']
                try:
                    json_data = json.loads(raw_response)
                    return json_data, json_response

                except json.JSONDecodeError:
                    return
            else:
                return
        except json.JSONDecodeError:
            return
    else:
        return
