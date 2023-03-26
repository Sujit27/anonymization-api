from copy import deepcopy
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from enum import Enum
import spacy
import uvicorn


def load_models():
    """
    load the models from disk
    and put them in a dictionary
    Returns:
        dict: loaded models
    """
    models = {
        "en_sm": spacy.load("/models/en_sm/")
        # "en_sm": spacy.load("/home/sujit/projects/models/en_sm/en_core_web_sm-3.0.0/")
    }
    print("models loaded from disk")
    return models


models = load_models()


class ModelLanguage(str, Enum):
    en = "en"


class ModelSize(str, Enum):
    sm = "sm"
    md = "md"
    lg = "lg"


class UserRequestIn(BaseModel):
    text: str
    model_language: ModelLanguage = "en"
    model_size: ModelSize = "sm"


class EntityOut(BaseModel):
    start: int
    end: int
    type: str
    text: str


class EntitiesOut(BaseModel):
    entities: List[EntityOut]
    anonymized_text: str

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Server is up !"}

@app.post("/entities", response_model=EntitiesOut)
def extract_entities(user_request: UserRequestIn):
    text = user_request.text
    language = user_request.model_language
    model_size = user_request.model_size

    model_key = language + "_" + model_size

    model = models[model_key]
    doc = model(text)

    entities = [
        {
            "start": ent.start_char,
            "end": ent.end_char,
            "type": ent.label_,
            "text": ent.text,
        }
        for ent in doc.ents
    ]

    anonymized_text = list(deepcopy(text))

    for entity in entities:
        start = entity["start"]
        end = entity["end"]
        anonymized_text[start:end] = "X" * (end - start)

    anonymized_text = "".join(anonymized_text)
    return {"entities": entities, "anonymized_text": anonymized_text}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, log_level="debug",workers=1)