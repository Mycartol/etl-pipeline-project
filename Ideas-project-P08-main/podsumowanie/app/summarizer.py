# summarizer.py
from fastapi import HTTPException
from app.openai_backend import generate_summary_with_openai, OpenAIQuotaError
from app.localai_backend import generate_summary_with_localai

def _build_narrative_prompt(diff_data: dict) -> str:
    """
    Tworzy z danych 'differences' prosty, zwięzły tekst do podsumowania.
    """
    parts = []

    for diff in diff_data.get("differences", []):
        t = diff.get("type")
        if t == "modified":
            old = diff.get("old_line", "").strip()
            new = diff.get("new_line", "").strip()
            # Combine old and new for modified lines more directly
            parts.append(f"Zmieniono: '{old}' na '{new}'.")
        elif t == "added":
            line = diff.get("line", "").strip()
            parts.append(f"Dodano nowy zapis: '{line}'.") # More descriptive
        elif t == "removed":
            line = diff.get("line", "").strip()
            parts.append(f"Usunięto zapis: '{line}'.") # More descriptive

    # Join all parts. Use a period and space for separation.
    narrative_content = " ".join(parts).strip()

    if not narrative_content:
        return "Brak istotnych zmian do podsumowania."

    # Final instruction to the model
    # Emphasize conciseness and key information
    prompt = f"Podsumuj te kluczowe zmiany w dokumencie w 2-3 zwięzłych zdaniach po polsku, skupiając się na najważniejszych modyfikacjach i nowych postanowieniach: {narrative_content}"
    return prompt

def summarize_diff_dict(diff_data: dict, backend: str = "openai") -> str:
    """
    Generuje podsumowanie na podstawie narracyjnego promptu.
    """
    try:
        prompt = _build_narrative_prompt(diff_data)

        if backend == "openai":
            try:
                return generate_summary_with_openai(prompt)
            except OpenAIQuotaError:
                # Fallback to localai if OpenAI quota is exceeded
                return generate_summary_with_localai(prompt)
        else: # backend == "localai"
            return generate_summary_with_localai(prompt)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))