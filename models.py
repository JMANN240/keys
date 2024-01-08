from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Item(Base):
	__tablename__ = "items"

	key = Column(String, primary_key=True, index=True)
	value = Column(String, nullable=False)
	prefix = Column(String, primary_key=True, nullable=True)