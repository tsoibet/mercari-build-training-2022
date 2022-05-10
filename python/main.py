import os
import logging
import pathlib
import json
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

FILENAME = "items.json"

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

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.get("/items")
def get_items():
    return load_file_to_json()

@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...)):
    write_json({"name": name, "category": category})
    logger.info(f"Receive item: {name}")
    return {"message": f"item received: {name}"}

@app.get("/image/{items_image}")
async def get_image(items_image):
    # Create image path
    image = images / items_image

    if not items_image.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)

def load_file_to_json():
    with open(FILENAME, 'r') as file:
        file_data = json.load(file)
    return file_data

def write_json(new_data):
    file_data = load_file_to_json()
    with open(FILENAME, 'w') as file:
        file_data["items"].append(new_data)
        json.dump(file_data, file)