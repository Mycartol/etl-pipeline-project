import os
from openai import OpenAI
from app.config import OPENAI_MODEL

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Definicja własnego wyjątku dla przekroczenia limitu zapytań lub niewystarczającego przydziału
class OpenAIQuotaError(Exception):
    """Wyjątek zgłaszany, gdy OpenAI zwróci błąd 429 (limit zapytań) lub niewystarczający przydział."""
    pass

def generate_summary_with_openai(text: str) -> str:
    """
    Wykorzystuje API OpenAI do wygenerowania podsumowania zmian.
    
    Parametry:
        text: str - tekst zawierający zmiany do podsumowania
    
    Zwraca:
        str - wygenerowane podsumowanie
    """
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "Jesteś pomocnym asystentem, który podsumowuje zmiany prawne."},
            {"role": "user",   "content": f"Podsumuj następujące zmiany:\n{text}"}
        ],
        temperature=0.3,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()
