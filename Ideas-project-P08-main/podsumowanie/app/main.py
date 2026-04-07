# Plik: podsumowanie/app/main.py

import os
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from app.models import SummaryResponse, AIBackend
from app.summarizer import summarize_diff_dict
from dotenv import load_dotenv

# 1. Ładujemy zmienne środowiskowe z pliku .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set in .env")

# 2. Tworzymy klienta MongoDB i wskazujemy bazę oraz kolekcje
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_default_database()  # domyślnie "document_tracker"
diffs_col = db.diffs
summaries_col = db.summaries

app = FastAPI(title="Podsumowywacz zmian LLM")


@app.post("/summarize-changes", response_model=SummaryResponse)
async def summarize_changes(
    url: str = Query(..., description="URL dokumentu"),
    backend: AIBackend = Query(default=AIBackend.openai, description="Wybierz 'openai' lub 'localai'")
):
    """
    Endpoint FastAPI, który:
     1. Dla podanego `url` pobiera najnowszy dokument `diff` z kolekcji `diffs`.
     2. Jeśli znaleziono, to wyciąga zawartość diff_content (format JSON), generuje podsumowanie.
     3. Uaktualnia wiersz `diff` w MongoDB, dopisując pole `description` = tekst podsumowania.
     4. Tworzy nowy dokument w kolekcji `summaries` (z polem wskazującym na źródłowy diff_id i typ backendu).
     5. Zwraca w odpowiedzi JSON z polami:
          - summary: wygenerowany tekst
          - mongo_id: id dokumentu utworzonego w `summaries`.
    """
    try:
        # 1. Pobierz najnowszy diff z MongoDB na podstawie URL
        latest_diff = diffs_col.find_one(
            {"url": url},
            sort=[("generated_at", -1)]
        )
        if not latest_diff:
            # Brak żadnego diff w bazie dla tego URL → 404
            raise HTTPException(status_code=404, detail=f"Brak diffów dla URL: {url}")

        # 2. Wyciągnij pole diff_content (to powinien być słownik lub lista różnic)
        diff_data = latest_diff.get("diff_content")
        if not diff_data:
            # Jeśli diff_content jest puste lub błędnego typu
            raise HTTPException(status_code=500, detail="Brak danych w polu 'diff_content' dla tego diffu")

        # 3. Generuj podsumowanie korzystając z odpowiedniego backendu (openai / localai)
        summary_text = summarize_diff_dict(diff_data, backend=backend.value)

        # 4. Zaktualizuj dokument `diff` w MongoDB, dopisując pole `description`
        diffs_col.update_one(
            {"_id": latest_diff["_id"]},
            {"$set": {"description": summary_text}}
        )

        # 5. Wstaw nowy dokument do kolekcji `summaries`
        record = {
            "url": url,
            "source_diff_id": latest_diff["_id"],
            "backend": backend.value,
            "summary": summary_text,
            "timestamp": datetime.utcnow()
        }
        insert_result = summaries_col.insert_one(record)
        mongo_id = str(insert_result.inserted_id)

        diffs_col.update_one(
            {"_id": latest_diff["_id"]},
            {"$set": {"description": summary_text}}
        )

        # 6. Zwróc odpowiedź (podsumowanie + id w kolekcji `summaries`)
        return SummaryResponse(
            summary=summary_text,
            mongo_id=mongo_id
        )

    except HTTPException:
        # Przekazujemy dalej wcześniej rzucone HTTPException (np. 404, 500 itp.)
        raise
    except Exception as e:
        # Każdy inny błąd traktujemy jako 500 Internal Server Error
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/summaries", response_model=list[SummaryResponse])
async def get_all_summaries():
    """
    Opcjonalny endpoint GET /summaries:
    Zwraca listę wszystkich zapisanych w kolekcji `summaries` dokumentów,
    posortowanych malejąco po dacie `timestamp`.
    """
    try:
        docs = summaries_col.find().sort("timestamp", -1)
        result = []
        for doc in docs:
            result.append(
                SummaryResponse(
                    summary=doc.get("summary", ""),
                    mongo_id=str(doc.get("_id"))
                )
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Komendy do budowania i uruchamiania serwisu w Dockerze:
'''
docker-compose down
docker-compose up --build -d
docker-compose build --no-cache api-frontend
docker-compose up -d

# Aby odbudować tylko mikroserwis "podsumowanie":
# docker compose up --build podsumowanie
'''
