from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from datetime import datetime
from hashlib import sha256
from bson.objectid import ObjectId
import requests
import os
import docker

app = Flask(__name__)

current_scraping_url = None

# Dla pobierania stanu kontenerów i CORS dla frontendu
docker_client = docker.from_env()
CORS(app)

# Konfiguracja MongoDB
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://repozytorium:27017/document_tracker")
mongo = PyMongo(app)

documents_col = mongo.db.documents
diffs_col = mongo.db.diffs


# Pomocnicza funkcja do tworzenia hash'a

def generate_hash(content):
    return sha256(content.encode('utf-8')).hexdigest()


# ENDPOINT: Zapis dokumentu (używany przez scraper)
@app.route("/api/documents", methods=["POST"])
def save_document():
    data = request.json
    url = data.get("url")
    content = data.get("content")

    if not url or not content:
        return jsonify({"error": "Missing url or content"}), 400

    content_hash = generate_hash(content)
    timestamp = datetime.utcnow()

    # Znajdź ostatnią wersję
    last_version = documents_col.find_one(
        {"url": url},
        sort=[("timestamp", -1)]
    )

    version = (last_version["version"] + 1) if last_version else 1

    # Zapisz nową wersję niezależnie od treści
    documents_col.insert_one({
        "url": url,
        "content": content,
        "timestamp": timestamp,
        "version": version,
        "hash": content_hash
    })

    return jsonify({"message": "Document saved.", "version": version}), 201


# ENDPOINT: Pobierz ostatnie dwie wersje dokumentu na podstawie URL
@app.route("/api/documents/latest", methods=["GET"])
def get_latest_versions():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    versions = list(documents_col.find(
        {"url": url},
        sort=[("timestamp", -1)]
    ).limit(2))

    if len(versions) < 2:
        return jsonify({"error": "Not enough versions to compare."}), 400

    return jsonify({
        "previous": versions[1],
        "latest": versions[0]
    })


# ENDPOINT: Zapisz różnice między wersjami (używany przez porównujący moduł)

@app.route("/api/diffs", methods=["POST"])
def save_diff():
    data = request.json
    print("Received raw body:", request.data)
    url = data.get("url")
    from_version = data.get("from_version")
    to_version = data.get("to_version")
    diff_content = data.get("diff_content")

    # Sprawdź, czy diff_content jest JSONem (słownikiem lub listą)
    if not isinstance(diff_content, (dict, list)):
        return jsonify({"error": "diff_content must be a JSON object or array"}), 400

    if not all([url, from_version, to_version, diff_content]):
        return jsonify({"error": "Missing required fields"}), 400

    diff_doc = {
        "url": url,
        "from_version": from_version,
        "to_version": to_version,
        "diff_content": diff_content,  # zapisujemy jako JSON (bson)
        "generated_at": datetime.utcnow()
    }

    inserted = diffs_col.insert_one(diff_doc)
    return jsonify({"message": "Diff saved.", "diff_id": str(inserted.inserted_id)}), 201


@app.route("/api/diffs/latest", methods=["GET"])
def get_latest_diff():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    latest_diff = diffs_col.find_one(
        {"url": url},
        sort=[("generated_at", -1)]
    )

    if not latest_diff:
        return jsonify({"error": "No diffs found for this url"}), 404

    latest_diff["_id"] = str(latest_diff["_id"])

    # diff_content już jest JSONem, więc zwracamy bez zmian
    return jsonify(latest_diff)


@app.route("/api/diffs", methods=["GET"])
def get_all_diffs_by_url():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    diffs = list(diffs_col.find({"url": url}).sort("generated_at", -1))
    for diff in diffs:
        diff["_id"] = str(diff["_id"])

    return jsonify(diffs)


@app.route("/api/diffs/<diff_id>", methods=["GET"])
def get_diff_by_id(diff_id):
    try:
        oid = ObjectId(diff_id)
    except Exception:
        return jsonify({"error": "Invalid diff_id"}), 400

    diff = diffs_col.find_one({"_id": oid})
    if not diff:
        return jsonify({"error": "Diff not found"}), 404

    diff["_id"] = str(diff["_id"])
    return jsonify(diff)


@app.route("/api/diffs/<diff_id>/description", methods=["POST"])
def save_diff_description(diff_id):
    data = request.json
    description = data.get("summary")
    if not description:
        return jsonify({"error": "Missing description"}), 400

    try:
        oid = ObjectId(diff_id)
    except Exception:
        return jsonify({"error": "Invalid diff_id"}), 400

    result = diffs_col.update_one(
        {"_id": oid},
        {"$set": {"description": description}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Diff not found"}), 404

    return jsonify({"message": "Description saved."}), 200


@app.route("/api/diffs/all", methods=["GET"])
def get_all_diffs():
    diffs_cursor = diffs_col.find({}, {"_id": 1, "url": 1, "generated_at": 1})
    diffs = list(diffs_cursor)

    if not diffs:
        return jsonify({"error": "No diffs found."}), 404

    for diff in diffs:
        diff["_id"] = str(diff["_id"])
        diff["generated_at"] = diff["generated_at"].isoformat()

    return jsonify(list(diffs))


@app.route("/api/diffs/<diff_id>/description", methods=["GET"])
def get_diff_description(diff_id):
    try:
        oid = ObjectId(diff_id)
    except Exception:
        return jsonify({"error": "Invalid diff_id"}), 400

    doc = diffs_col.find_one({"_id": oid}, {"description": 1})

    if not doc:
        return jsonify({"error": "Diff not found"}), 404

    return jsonify({"description": doc.get("description", "Summary is not available for this URL.")}), 200


@app.route("/api/urls", methods=["GET"])
def get_all_urls():
    urls = documents_col.distinct("url")
    return jsonify(urls), 200


# Odpala kontener z akwizycją (zapewne do zmiany, ale by można było coś pokazać)
def start_container(url, container_name):
    containers = {
        "akwizycja": "ideas-project-p08-akwizycja:latest",
        "wersjonowanie": "ideas-project-p08-wersjonowanie:latest",
        "podsumowanie": "ideas-project-p08-podsumowanie:latest"
    }

    try:
        container = None
        for c in docker_client.containers.list(all=True, filters={"name": container_name}):
            container = c
            break

        if container:
            if container.status == "running":
                container.stop()
            container.remove()

        container = docker_client.containers.run(
            image=containers[container_name],
            name=container_name,  # stała nazwa
            detach=True,
            ports={"5000/tcp": None},
            network="ideas-project-p08_default",
            environment={
                "SCRAP_URL": url
            }
        )

    except docker.errors.APIError as e:
        app.logger.error(f"Docker API error: {e}")
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")


@app.route("/api/start", methods=["POST"])
def start_process():
    data = request.json
    if not data or "url" not in data:
        return jsonify({"error": "Missing URL in request body"}), 400

    scrap_url = data.get("url")
    start_container(scrap_url, "akwizycja")

    return jsonify({
        "message": "Akwizycja started",
    }), 200


@app.route("/api/trigger-next", methods=["POST"])
def trigger_next_stage():
    data = request.json
    if not data or "url" not in data:
        return jsonify({"error": "Missing URL in request body"}), 400

    scrap_url = data.get("url")
    start_container(scrap_url, "wersjonowanie")

    return jsonify({
        "message": "Wersjonowanie started",
    }), 200


# Zbiera obecny status 3 pierwszych modułów, by odpowiednio wyświetlić na frontendzie
@app.route("/api/status", methods=["GET"])
def get_status():
    try:
        containers = docker_client.containers.list(all=True)

        # Nazwy etapów, które Cię interesują
        stages = ["akwizycja", "wersjonowanie", "podsumowanie"]

        status = {}

        for c in containers:
            for stage in stages:
                if stage in c.name:
                    status[c.name] = c.status
                    break  # nie sprawdzaj dalej – już przypasował

        current_stage = "idle"

        for stage in stages:
            for name, state in status.items():
                if stage in name and state == "running":
                    current_stage = stage
                    break
            if current_stage != "idle":
                break

        return jsonify({
            "current_stage": current_stage,
            "containers_status": status
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Pobranie zmian z modułu podsumowania dla frontendu (na razie przykładowe, co jest w podsumowanie/samples)
@app.route("/api/summary", methods=["POST"])
def get_summary():
    urls = diffs_col.distinct("url")

    for url in urls:
        try:
            response = requests.post(f"http://podsumowanie:5000/summarize-changes?url={url}", timeout=10)
            if response.status_code == 200:
                summary_data = response.json()
                print(f"Summary for {url}: {summary_data}")
            else:
                print(f"Failed to fetch summary for {url}: {response.status_code}")
        except requests.RequestException as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Summary fetched successfully"}), 200


@app.route("/api/current-url", methods=["GET"])
def get_current_scraping_url():
    return jsonify({"current_url": current_scraping_url})


@app.route("/api/current-url-update", methods=["POST"])
def update_current_scraping_url():
    global current_scraping_url
    data = request.json
    print(data)
    current_scraping_url = data.get("url", None)
    return jsonify({"message": "URL updated"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
