# localai_backend.py
import torch
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# 1. Model mT5-small (obsługuje polski)
MODEL_ID = "google/mt5-small"

# 2. Konfiguracja urządzenia (GPU/CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device_id = 0 if torch.cuda.is_available() else -1

# 3. Wczytujemy „wolny” tokenizer, by uniknąć błędu z protobuf
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=False)
model     = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID).to(device)

# 4. Inicjalizacja pipeline("summarization")
summarizer = pipeline(
    "summarization",
    model=model,
    tokenizer=tokenizer,
    device=device_id
)

def generate_summary_with_localai(prompt: str) -> str:
    """
    Generuje podsumowanie lokalnie przy użyciu google/mt5-small.
    - Dokleja prefiks "summarize: " (potrzebne, by pipeline dobrze działał).
    - Zwiększa min_length, żeby uzyskać co najmniej kilka zdań.
    """
    # 1. Dodajemy wymagany prefiks
    input_prompt = "summarize: " + prompt

    # 2. Wywołujemy pipeline("summarization") z beam search
    result = summarizer(
        input_prompt,
        max_length=150, # Slightly reduced max_length
        min_length=30,    # SIGNIFICANTLY reduced min_length
        do_sample=False,  # beam search
        num_beams=4,
        length_penalty=1.0,
        early_stopping=True,
        no_repeat_ngram_size=3 # ADD THIS LINE - very important for repetition
    )
    # 3. Pobieramy wygenerowany tekst, usuwamy ewentualne tokeny <extra_id_*>
    summary = result[0]["summary_text"].strip()
    # Clean up <extra_id_*> tokens more aggressively if they still appear
    summary = re.sub(r"<extra_id_\d+>", "", summary).strip()
    # Remove leading/trailing non-alphanumeric characters or excessive punctuation
    summary = re.sub(r"^[^\w\s]+|[^\w\s]+$", "", summary)
    # Remove multiple consecutive non-alphanumeric characters (like :::::)
    summary = re.sub(r"([^\w\s])\1+", r"\1", summary)
    # If the summary is still too short or empty after cleaning, provide a fallback
    if len(summary) < 20: # If summary is very short, it might be garbage
        return "Podsumowanie lokalne niedostępne lub niskiej jakości. Spróbuj ponownie z OpenAI."

    return summary