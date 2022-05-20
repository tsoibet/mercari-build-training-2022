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
SCHEMA_NAME = "../db/items.db"
ERR_MSG = "ERROR"
image_dir = pathlib.Path(__file__).parent.resolve() / "image"

logger = logging.getLogger("uvicorn")
logger.setLevel(os.environ.get('LOGLEVEL', 'INFO').upper())

try:
    conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
    logger.info("Connected to database.")
except Exception as e:
    logger.error(f"Failed to connect to database. Error message: {e}")

app = FastAPI()

origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

@app.on_event("startup")
def init_database():
    try:
        cur = conn.cursor()
        with open(SCHEMA_NAME) as schema_file:
            schema = schema_file.read()
            logger.debug("Read schema file.")
        cur.executescript(f'''{schema}''')
        add_sample_data()
        conn.commit()
        logger.info("Completed database initialization.")
    except Exception as e:
        logger.warn(f"Failed to initialize database. Error message: {e}")

def add_sample_data():
    try:
        cur = conn.cursor()
        cur.execute('''SELECT id FROM category''')
        category_result = cur.fetchone()
        if (category_result is None):
            SAMPLE_CATEGORY_LIST = [("Fashion", ), ("Toy", ), ("Instrument", )]
            SAMPLE_ITEM_LIST = [("Hat", 1, "sample1.jpg"), ("Teddy Bear", 2, "sample2.jpg"), ("Guitar", 3, "sample3.jpg")]
            cur.executemany('''INSERT INTO category(name) VALUES (?)''', SAMPLE_CATEGORY_LIST)
            cur.executemany('''INSERT INTO items(name, category_id, image_filename) VALUES (?, ?, ?)''', SAMPLE_ITEM_LIST)
            logger.debug("Added sample data.")
        else:
            logger.debug("Data exists. No need to add sample data.")
    except Exception as e:
        logger.warn(f"Failed to add sample data. Error message: {e}")
        return ERR_MSG

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.get("/items")
def get_items():
    logger.info("Received get_items request.")
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT items.id, items.name, category.name as category, items.image_filename 
            FROM items INNER JOIN category 
            ON category.id = items.category_id
        ''')
        items = cur.fetchall()
        item_list = [dict(item) for item in items]
        items_json = {"items": item_list}
        logger.info("Returning all items.")
        return items_json
    except Exception as e:
        logger.warn(f"Failed to get items. Error message: {e}")   
        return ERR_MSG

@app.get("/items/{item_id}")
def get_item(item_id: int):
    logger.info(f"Received get_item request of item id: {item_id}.")
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT items.id, items.name, category.name as category, items.image_filename 
            FROM items INNER JOIN category 
            ON category.id = items.category_id 
            WHERE items.id = (?)
        ''', (item_id, ))
        item_result = cur.fetchone()
        if (item_result is None):
            raise HTTPException(status_code=404, detail="Item not found")
        logger.info(f"Returning the item of id: {item_id}.")
        return item_result
    except HTTPException:
        logger.info("Failed to get item: Item not found")
        return "Item not found"
    except Exception as e:
        logger.warn(f"Failed to get item. Error message: {e}")
        return ERR_MSG

@app.delete("/items/{item_id}")
def get_item(item_id: int):
    logger.info(f"Received delete_item request of item id: {item_id}.")
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''SELECT name FROM items WHERE id = (?)''', (item_id, ))
        item_result = cur.fetchone()
        if (item_result is None):
            raise HTTPException(status_code=404, detail="Item not found")
        cur.execute('''DELETE FROM items WHERE id = (?)''', (item_id, ))
        conn.commit()
        logger.info(f"Deleted item {item_result[0]} of id: {item_id}.")
        return {"message": f"Deleted item {item_result[0]} of id: {item_id}."}
    except HTTPException:
        logger.info("Failed to delete item: Item not found")
        return "Item not found"
    except Exception as e:
        logger.warn(f"Failed to get item. Error message: {e}")
        return ERR_MSG

@app.post("/items")
async def add_item(name: str = Form(..., max_length=32), category: str = Form(..., max_length=12), image: UploadFile = File(...)):
    logger.info(f"Received add_item request.")

    if image.content_type != "image/jpeg":
        raise HTTPException(400, detail="Image not in jpg format.")

    try:
        cur = conn.cursor()

        image_binary = await image.read()
        new_image_name = hashlib.sha256(image_binary).hexdigest() + ".jpg"
    
        image_path = image_dir / new_image_name
        with open(image_path, 'wb') as image_file:
            image_file.write(image_binary)

        cur.execute('''SELECT id FROM category WHERE name = (?)''', (category, ))
        category_result = cur.fetchone()
        if (category_result is None):
            cur.execute('''INSERT INTO category(name) VALUES (?) RETURNING id''', (category, ))
            category_result = cur.fetchone()
        cur.execute('''INSERT INTO items(name, category_id, image_filename) VALUES (?, ?, ?)''', (name, category_result[0], new_image_name))
        conn.commit()
        logger.info(f"Item {name} of {category} category is added into database.")
        return {"message": f"Item {name} of {category} category is received."}
    except Exception as e:
        logger.warn(f"Failed to add item. Error message: {e}")
        return ERR_MSG

@app.get("/search")
def search_item(keyword: str):
    logger.info(f"Received search_item request of search keyword: {keyword}.")
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT items.id, items.name, category.name as category, items.image_filename 
            FROM items INNER JOIN category 
            ON category.id = items.category_id 
            WHERE items.name LIKE (?)
        ''', (f"%{keyword}%", ))
        items = cur.fetchall()
        item_list = [dict(item) for item in items]
        items_json = {"items": item_list}
        logger.info(f"Returning items with name containing {keyword}.")
        return items_json
    except Exception as e:
        logger.warn(f"Failed to search items. Error message: {e}")
        return ERR_MSG

@app.get("/image/{image_filename}")
async def get_image(image_filename: str):
    logger.debug(f"API endpoint get_image is called.")
    # Create image path
    image = image_dir / image_filename

    if not image_filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.info(f"Image not found: {image}")
        image = image_dir / "default.jpg"

    return FileResponse(image)

@app.on_event("shutdown")
def disconnect_database():
    try:
        conn.close()
        logger.info("Disconnected database.")
    except Exception as e:
        logger.error(f"Failed to disconnect database. Error message: {e}")