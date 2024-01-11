from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

import models
from schemas import ValidatedKey

def get_value_strict(db: Session, validatedKey: ValidatedKey, owner: UUID) -> Optional[models.Item]:
	return db.query(models.Item).filter(models.Item.key == validatedKey.key, models.Item.owner == str(owner)).first()

def get_value(db: Session, validatedKey: ValidatedKey, owner: UUID) -> Optional[models.Item]:
	while True:
		item: Optional[models.Item] = get_value_strict(db, validatedKey, owner)
		if item is not None:
			return item
		validatedKey = validatedKey.get_parent_key()
		if validatedKey is None:
			return None

def set_value(db: Session, validatedKey: ValidatedKey, owner: UUID, value: str) -> None:
	item: Optional[models.Item] = get_value_strict(db, validatedKey, owner)
	if item is not None:
		item.value = value
	else:
		db.add(models.Item(key=validatedKey.key, value=value, owner=str(owner)))
	db.commit()


def del_value(db: Session, validatedKey: ValidatedKey, owner: UUID) -> None:
	item: Optional[models.Item] = get_value_strict(db, validatedKey, owner)
	if item is not None:
		db.delete(item)
