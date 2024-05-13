from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Annotated, List
from sqlalchemy.orm import Session
from uuid import UUID
from database import SessionLocal, engine
import models

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = {
    "http://localhost:3000",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

class ToDoBase(BaseModel):
    title: str
    description: str
    completed: bool = False

class ToDoModel(ToDoBase):
    id: int

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

models.Base.metadata.create_all(bind=engine)

# create todo
@app.post("/todos/", response_model=ToDoModel)
async def create_todo(todo: ToDoBase, db: Session= Depends(get_db)):
    db_todo = models.Todos(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo




# get todos
@app.get("/todos/", response_model=List[ToDoModel])
async def read_todos(db: db_dependency, skip: int = 0, limit: int = 100):
    todos = db.query(models.Todos).offset(skip).limit(limit).all()
    return todos

# delete todo
@app.delete("/todos/{todo_id}", response_model=ToDoModel)
async def delete_todo(todo_id: int, db: db_dependency):
    db_todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return db_todo

# update todo
@app.put("/todos/{todo_id}", response_model=ToDoModel)
async def update_todo(todo_id: int, todo: ToDoBase, db: db_dependency):
    db_todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    # update the todo item with the new values
    for key, value in todo.dict().items():
        setattr(db_todo, key, value)

    db.commit()
    db.refresh(db_todo)
    return db_todo

# mark a todo as complete
@app.put("/todos/{todo_id}/complete", response_model=ToDoModel)
async def complete_todo(todo_id: int, db: db_dependency):
    db_todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    # mark todo item as completed
    db_todo.completed = True

    db.commit()
    db.refresh(db_todo)
    return db_todo
