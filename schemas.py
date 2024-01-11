import re
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, field_validator

class ValidatedKey(BaseModel):
	key: str

	@field_validator('key')
	@classmethod
	def is_valid_key(cls, key: str) -> str:
		assert re.search('^\w+(?:.\w+)*$', key) is not None, f"'{key}' is not a valid key"
		return key

	def get_parent_key(self) -> Optional['ValidatedKey']:
		parent_components: List[str] = self.key.split('.')[:-1]

		if len(parent_components) == 0:
			return None

		return ValidatedKey(key='.'.join(parent_components))

class EntitySchema(BaseModel):
	uuid: UUID
	name: str
