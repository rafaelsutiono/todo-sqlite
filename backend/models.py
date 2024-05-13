from database import Base
from sqlalchemy import Column, String, Boolean, Integer

class Todos(Base):
    __tablename__ = 'todo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    description = Column(String)
    completed = Column(Boolean)
