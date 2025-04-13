import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")

points = """
Сбор средств на покупку нового автомобиля.
Строительство нового дома для детского дома.
Сбор средств на создание завода для производства сигарет.
Организация международной гуманитарной помощи в зонах бедствия.
Строительство спортивного комплекса в небольшом городе.
Создание бизнес-стартапа в сфере экологических технологий.
Разработка нового оружия для военных нужд.
Сбор средств на проведение роскошной свадьбы.
Разработка косметики, тестируемой на животных.
Сбор средств для финансирования частной школы для элиты.
"""

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

Ответ должен быть в виде списка объектов JSON с полями id, valid и reason. Не должно быть другого текста.

Пример ответа:
[
    {{ "id": 1, "valid": "false", "reason": "Преследует личные цели: покупка автомобиля" }},
    {{ "id": 2, "valid": "true", "reason": "Благотворительность: постройка детского дома" }}
]

Вот цели:
{points}
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
                print("Ответ в формате JSON:", json_data)

                with open('output.json', 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                print("Не удалось распарсить строку как JSON, ответ от сервера:")
                print(raw_response)
        else:
            print("Ответ не содержит ожидаемый формат JSON. Ожидался объект с ключом 'response'.")
            print("Ответ от сервера:", response.text)
    except json.JSONDecodeError:
        print("Не удалось распарсить JSON, ответ от сервера:")
        print(response.text)
else:
    print(f"Ошибка при запросе, статус: {response.status_code}")
