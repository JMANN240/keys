from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

import models

def get_entity_by_uuid(db: Session, uuid: UUID) -> Optional[models.Entity]:
	return db.query(models.Entity).filter(models.Entity.uuid == uuid).first()

def get_entity_by_name(db: Session, name: str) -> Optional[models.Entity]:
	return db.query(models.Entity).filter(models.Entity.name == name).first()

def create_entity(db: Session, name: str) -> models.Entity:
	entity: Optional[models.Entity] = get_entity_by_name(db, name)
	if entity is None:
		entity = models.Entity(uuid=str(uuid4()), name=name)
		db.add(entity)
		db.commit()
	return entity

def del_entity(db: Session, uuid: UUID) -> None:
	entity: Optional[models.Entity] = get_entity_by_uuid(db, uuid)
	if entity is not None:
		db.delete(entity)
