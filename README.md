# secscandb

This is a lightweight web API built with **FastAPI** and **PickleDB**.
Each project is stored in its own PickleDB database file on disk.
Each key in a project maps to a JSON object.

---

## Installation

1. **Clone the repository** (or download the source code)

2. **Install dependencies**

```bash
pip install -r requirements.txt
````

---

## Running the Application

Run the FastAPI app using `uvicorn`:

```bash
uvicorn main:app --reload
```

The API will be available at:
[http://localhost:8000](http://localhost:8000)

The interactive API docs are available at:
[http://localhost:8000/docs](http://localhost:8000/docs)

---

## Project Data Storage

* All project data is stored under the `data/` folder
* Each project has its own subdirectory and `db.json` file

---

## API Endpoints

### 1. `GET /list_projects`

Lists all existing projects (folder names under `data/`).

```bash
curl http://localhost:8000/list_projects
```

---

### 2. `GET /get_project/{project}`

Returns all key-value records (JSON objects) in the specified project.

```bash
curl http://localhost:8000/get_project/my_project
```

---

### 3. `POST /upsert_data`

Creates or updates a key-value record in a project. The request payload must contain an object with the fields `title` and `loc`, which are hashed to create the record unique key

#### Request Body (JSON)

```json
{
  "project": "my_project",
  "object": {
    "title" : "title of doc",
    "loc"   : "unique location",
    "field1": "value1",
    "field2": "value2"
  }
}
```

#### Example cURL

```bash
curl -X POST http://localhost:8000/upsert_data \
  -H "Content-Type: application/json" \
  -d '{
    "project": "alpha",
    "object": {
      "title" : "Test1",
      "loc": "somewhere",
      "name": "Widget",
      "status": "new"
    }
  }'
```

The database record key is generated from a hash of the title and location. If it already exists, the fields will be merged (updated).
If the key does not exist, a new key will be created and the object payload saved.

---

## Requirements

* Python 3.7+
* FastAPI
* PickleDB
* Uvicorn (for development server)
