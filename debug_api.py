import requests
import json

# ЗАМЕНИ на реальный аккаунт, который решает задачи без рейтинга
username = "sweet_bun"

url = f"https://lichess.org/api/user/{username}/activity"
resp = requests.get(url, headers={"Accept": "application/json"})
print(f"Статус: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    # Выводим всё (может быть много, но нам важно найти "puzzles" с "day")
    print(json.dumps(data, indent=2, ensure_ascii=False))
else:
    print("Ошибка:", resp.text)
