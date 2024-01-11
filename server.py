import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from config import *
import entities
import keys
import models
from database import SessionLocal, engine
from schemas import ValidatedKey, EntitySchema

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

@app.get('/favicon.ico')
async def get_favicon():
	return

api = FastAPI()

# Keys things

async def validate_key(key: str):
	return ValidatedKey(key=key)

ValidatedKeyDep = Annotated[ValidatedKey, Depends(validate_key)]

@api.get('/keys', response_class=PlainTextResponse)
async def api_get_value(key: ValidatedKeyDep, owner: UUID, db: Session = Depends(get_db)):
	item = keys.get_value(db, key, owner)
	if item is not None:
		return item.value
	return None

@api.post('/keys')
async def api_set_value(key: ValidatedKeyDep, owner: UUID, value: str, db: Session = Depends(get_db)):
	if owner is None:
		raise HTTPException(401)
	keys.set_value(db, key, value, owner)

@api.delete('/keys')
async def api_delete_value(key: ValidatedKeyDep, owner: UUID, db: Session = Depends(get_db)):
	keys.del_value(db, key, owner)

# Entities things

@api.get('/entities', response_model=EntitySchema)
async def api_get_entity(uuid: UUID, db: Session = Depends(get_db)):
	return entities.get_entity_by_uuid(db, uuid)

@api.post('/entities', response_model=EntitySchema)
async def api_create_entity(name: str, db: Session = Depends(get_db)):
	entity = entities.create_entity(db, name)
	print(entity)
	return entity

@api.delete('/entities')
async def api_delete_entity(uuid: UUID, db: Session = Depends(get_db)):
	return entities.del_entity(db, uuid)

# Mount the API

app.mount('/api', api)