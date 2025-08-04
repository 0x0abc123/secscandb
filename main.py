import os
import re
import hashlib
import json
from pickledb import PickleDB
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()
DATA_DIR = "data"

os.makedirs(DATA_DIR, exist_ok=True)

# --- Models ---
class UpsertPayload(BaseModel):
    project: str
    #key: str | None = None  # optional; if not provided, a new UUID is created
    object: Dict[str, Any]

# --- Helpers ---
def sanitise_string(s: str):
    clean_text = re.sub(r'[^a-zA-Z0-9]', '_', s)
    return clean_text

def hash_string(s: str):
    encoded_string = s.encode('utf-8')
    sha256_hash_object = hashlib.sha256(encoded_string)
    return sha256_hash_object.hexdigest()

def get_project_db(project: str) -> PickleDB:
    project_path = os.path.join(DATA_DIR, sanitise_string(project))
    os.makedirs(project_path, exist_ok=True)
    db_path = os.path.join(project_path, "db.json")
    return PickleDB(db_path)
    #return pickledb.load(db_path, auto_dump=True)

# --- Endpoints ---

@app.get("/list_projects", response_model=List[str])
def list_projects():
    return [name for name in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, name))]

@app.get("/get_project/{project}", response_model=Dict[str, Any])
def get_project(project: str):
    try:
        db = get_project_db(project)
        return {key: json.loads(db.get(key)) for key in db.all()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading project: {e}")

@app.post("/upsert_data", response_model=Dict[str, Any])
def upsert_data(payload: UpsertPayload):
    db = get_project_db(payload.project)

    if payload.object is None:
        return {"error":"payload object missing"}
    title = payload.object.get('title')
    location = payload.object.get('loc')
    if title is None or location is None:
        return {"error":"payload object missing title or location"}
    payload_key = hash_string(f"{title}::{location}")
    existing = db.get(payload_key)
    if existing is not None:
        existing_obj = json.loads(existing)
        existing_obj.update(payload.object)
        db.set(payload_key, json.dumps(existing_obj))
        db.save()
        return {"key": payload_key, "updated": True, "value": existing_obj}
    else:
        db.set(payload_key, json.dumps(payload.object))
        db.save()
        return {"key": payload_key, "created": True, "value": payload.object}
