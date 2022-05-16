import os
import logging
import pathlib
import json
import sqlite3
import hashlib
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

DATABASE_NAME = "../db/mercari.sqlite3"

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "image"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

@app.on_event("startup")
def database_connect():
    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.cursor()
    with open('../db/items.db') as schema_file:
        schema = schema_file.read()
    cur.executescript(f'''{schema}''')
    conn.commit()
    logger.info("Database initialization complete.")
    conn.close()

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.get("/items")
def get_items():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('''SELECT items.name, category.name as category, items.image as image_filename FROM items INNER JOIN category ON category.id = items.category_id''')
    items = cur.fetchall()
    item_list = [dict(item) for item in items]
    items_json = {"items": item_list}
    conn.close()
    logger.info("Get items")
    return items_json

@app.get("/items/{item_id}")
def get_item(item_id):
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('''SELECT items.name, category.name as category, items.image FROM items INNER JOIN category ON category.id = items.category_id WHERE items.id = (?)''', (item_id, ))
    logger.info(f"Get item of id:")
    return cur.fetchone()


@app.post("/items")
async def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):
    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.cursor()

    image_binary = await image.read()
    new_image_name = hashlib.sha256(image_binary).hexdigest() + ".jpg"
    
    image_path = "./image/" + new_image_name
    with open(image_path, 'wb') as image_file:
        image_file.write(image_binary)

    cur.execute('''INSERT OR IGNORE INTO category(name) VALUES (?)''', (category, ))
    cur.execute('''SELECT id FROM category WHERE name = (?)''', (category, ))
    category_id = cur.fetchone()[0]
    cur.execute('''INSERT INTO items(name, category_id, image) VALUES (?, ?, ?)''', (name, category_id, new_image_name))
    conn.commit()
    conn.close()
    logger.info(f"Receive item: {name}")
    return {"message": f"item received: {name}"}


@app.get("/search")
def search_item(keyword: str):
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('''SELECT items.name, category.name as category, items.image FROM items INNER JOIN category ON category.id = items.category_id WHERE items.name LIKE (?)''', (f"%{keyword}%", ))
    items = cur.fetchall()
    item_list = [dict(item) for item in items]
    items_json = {"items": item_list}
    conn.close()
    logger.info(f"Get items with name containing {keyword}")
    return items_json


@app.get("/image/{image_filename}")
async def get_image(image_filename):
    # Create image path
    image = images / image_filename

    if not image_filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.info(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)