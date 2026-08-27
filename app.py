import os, json, base64, requests
from fastapi import FastAPI, HTTPException, status
from typing import List, Optional
import time

app = FastAPI()
TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO")
URL = f"https://api.github.com/repos/{REPO}/contents/books.json"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}

# Add retry mechanism
def get_with_retry(max_retries=3):
    for i in range(max_retries):
        try:
            r = requests.get(URL, headers=HEADERS, timeout=5)
            if r.status_code == 404:
                return [], None  # File doesn't exist
            if r.status_code == 200:
                data = r.json()
                content = base64.b64decode(data["content"]).decode()
                books = json.loads(content)
                return books if isinstance(books, list) else [], data.get("sha")
        except:
            if i == max_retries - 1:
                raise
            time.sleep(1)
    raise HTTPException(500, "Failed to fetch data")

@app.get("/books")
def get_books():
    books, _ = get_with_retry()
    return books

@app.post("/books")
def add_book(book: dict):
    # Basic validation
    if "title" not in book or "author" not in book:
        raise HTTPException(400, "Missing 'title' or 'author'")
    
    # Get current data with retry
    books, sha = get_with_retry()
    
    # Add book with unique ID
    book["id"] = max([b.get("id", 0) for b in books], default=0) + 1
    books.append(book)
    
    # Save with retry (race condition still possible but less likely)
    content = base64.b64encode(
        json.dumps(books, ensure_ascii=False, indent=2).encode()
    ).decode()
    
    r = requests.put(
        URL, headers=HEADERS,
        json={"message": "Add book", "content": content, "sha": sha},
        timeout=5
    )
    
    if r.status_code not in [200, 201]:
        raise HTTPException(r.status_code, r.text)
    
    return {"success": True, "book": book, "id": book["id"]}
