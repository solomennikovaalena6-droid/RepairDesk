import os
import requests
from dotenv import load_dotenv

load_dotenv()

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "repairdesk-agent")

SYSTEM_PROMPT = "Ты — ИИ-помощник приложения RepairDesk. Отвечай кратко и по делу."

class AgentError(Exception):
    pass

def ask_agent(history, user_text):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history[-10:])
    messages.append({"role": "user", "content": user_text})

    headers = {"Content-Type": "application/json"}
    payload = {"model": LLM_MODEL, "messages": messages, "temperature": 0.7, "max_tokens": 500}

    try:
        resp = requests.post(f"{LLM_BASE_URL.rstrip('/')}/chat/completions", json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.ConnectionError:
        raise AgentError("Ollama не запущена. Запустите её и попробуйте снова.")
    except requests.exceptions.Timeout:
        raise AgentError("Агент не ответил вовремя.")
    except Exception:
        raise AgentError("Ошибка при обращении к ИИ.")