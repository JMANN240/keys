from functools import wraps
import logging
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from config import *
import models
from database import SessionLocal, engine

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

def get_key_strict(db: Session, key: str, prefix: Optional[str]):
	logger.info(f"Getting {prefix}/{key} (strict).")
	return db.query(models.Item).filter(models.Item.key == key, models.Item.prefix == prefix).first()

def get_key(db: Session, key: str, prefix: Optional[str] = None):
	logger.info(f"Getting {prefix}/{key}.")
	if prefix is not None:
		prefixed_key_value = get_key_strict(db, key, prefix)

		if prefixed_key_value is not None:
			logger.debug(f"Found {prefix}/{key}!")
			return prefixed_key_value
		else:
			logger.debug(f"{prefix}/{key} does not exist, defaulting to {None}/{key}.")

	return get_key_strict(db, key, None)

def set_key(db: Session, key: str, value: str, prefix: Optional[str] = None):
	logger.info(f"Setting {prefix}/{key}")
	prefixed_key = get_key_strict(db, key, prefix)

	if prefixed_key is not None:
		logger.info(f"Updating {prefix}/{key} = {value}")
		prefixed_key.value = value
	else:
		logger.info(f"Inserting {prefix}/{key} = {value}")
		db.add(models.Item(key=key, value=value, prefix=prefix))

	db.commit()

@app.get('/favicon.ico')
async def get_favicon():
	return

@app.get('/{key}', response_class=PlainTextResponse)
async def api_get_key(key: str, db: Session = Depends(get_db), authorization: Annotated[Optional[str], Header()] = None):
	if authorization is None:
		raise HTTPException(401)
	if authorization != SECRET_KEY:
		raise HTTPException(403)
	item = get_key(db, key, None)
	if item is not None:
		return item.value
	return item

@app.get('/{prefix}/{key}', response_class=PlainTextResponse)
async def api_get_prefixed_key(prefix: str, key: str, db: Session = Depends(get_db), authorization: Annotated[Optional[str], Header()] = None):
	if authorization is None:
		raise HTTPException(401)
	if authorization != SECRET_KEY:
		raise HTTPException(403)
	item = get_key(db, key, prefix)
	if item is not None:
		return item.value
	return item

@app.post('/{key}/{value}')
async def api_set_key(key: str, value: str, db: Session = Depends(get_db), authorization: Annotated[Optional[str], Header()] = None):
	if authorization is None:
		raise HTTPException(401)
	if authorization != SECRET_KEY:
		raise HTTPException(403)
	set_key(db, key, value, None)

@app.post('/{prefix}/{key}/{value}')
async def api_set_prefixed_key(prefix: str, key: str, value: str, db: Session = Depends(get_db), authorization: Annotated[Optional[str], Header()] = None):
	if authorization is None:
		raise HTTPException(401)
	if authorization != SECRET_KEY:
		raise HTTPException(403)
	set_key(db, key, value, prefix)