import requests

key = "sk-2c8d218540ef4cb6a24bbcdfdac80c1d" # Твой ключ
url = "https://api.deepseek.com/chat/completions"

headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
data = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Привет, напиши 1 факт о Fallout"}]
}

try:
    res = requests.post(url, json=data, headers=headers)
    print(res.json())
except Exception as e:
    print(f"Ошибка: {e}")