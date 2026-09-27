from typing import Annotated
from dotenv import load_dotenv
from contextlib import asynccontextmanager


import os
load_dotenv()
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

DATABASE_URL = os.getenv("DATABASE_URL")

class Table_supabase(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at : int = Field(index=True)
    message_sent : str


engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(lifespan=lifespan)

@app.post("/")
def message_sent(message_sent: Table_supabase, session: SessionDep) -> Table_supabase:
    session.add(message_sent)
    session.commit()
    session.refresh(message_sent)
    return message_sent

@app.get("/")
def read_end_messages(session: SessionDep):
    end_message = session.exec(select(Table_supabase).order_by(Table_supabase.id.desc()).limit(1)).all()
    return end_message
