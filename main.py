from fastapi import Depends, FastAPI, HTTPException  # Import FastAPI and related modules.
from pydantic import BaseModel, EmailStr  # Import Pydantic BaseModel and Email validation type.
from typing import List  # Import List for type hinting.
from sqlalchemy import create_engine, Column, Integer, String  # SQLAlchemy utilities for ORM mapping.
from sqlalchemy.ext.declarative import declarative_base  # Base class for SQLAlchemy models.
from sqlalchemy.orm import sessionmaker, Session  # Session and sessionmaker for database operations.

DATABASE_URL = "mysql://root:123@localhost/book_management" #configure sqlalchemy

#Engine and session maker
engine = create_engine(DATABASE_URL, connect_args={"charset": "utf8mb4"})  #SQLAlchemy engine with charset.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  #session factory for managing DB sessions.

Base = declarative_base()  #base class for model definition

class Book(Base):

    __tablename__ = "books"  # Table name in the database.
    id = Column(Integer, primary_key=True, index=True)  # Primary key column w index.
    title = Column(String(255), nullable=False)  # Title column
    author = Column(String(255), nullable=False)  # Author column
    published_year = Column(Integer, nullable=False)  # Published year column
    genre = Column(String(255), nullable=True)  # Genre column, optional.
    isbn = Column(String(255), unique=True, nullable=False)  # ISBN column, unique identification

app = FastAPI()  #instance of FastAPI

# DB session dependency
def get_db():
    db = SessionLocal()  #creates new session
    try:
        yield db  # yield to endpoint func
    finally:
        db.close()  # close session after request

# Data model for a Book (Pydantic) for validation, so proper input is given only
class BookCreate(BaseModel):
    title: str  # Title ,string
    author: str  # Author ,string.
    published_year: int  # Published year , integer.
    genre: str  # Genre ,string.
    isbn: str  # ISBN ,string.

#pydantic schema for returning of book information, includes bookID
class BookOut(BookCreate):
  
    id: int  # book id, integer

    class Config:
        orm_mode = True  # Enable automatic conversion of ORM objects to dict.

# creates table if doesnt exist
Base.metadata.create_all(bind=engine)  # auto create books table in the db.

#ROUTES
#retireves all books, retuens as a list
@app.get("/books", response_model=List[BookOut])
def get_books(db: Session = Depends(get_db)):

    books = db.query(Book).all()  # get all books from db
    return books  # returns a list of books

#get a specific book by id. 404 if not found
@app.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    
    book = db.query(Book).filter(Book.id == book_id).first()  # Query the book by ID
    if not book:  # ifnot found give 404 error
        raise HTTPException(status_code=404, detail="Book not found")
    return book  # returns book data

#creates a new book and accepts data as input, adds to db and returns whats created
@app.post("/books", response_model=BookOut)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
   
    db_book = Book(
        title=book.title,  #sets the book title
        author=book.author,  # sets the author of the book
        published_year=book.published_year,  # set the year published 
        genre=book.genre,  # sets the book's genre
        isbn=book.isbn,  #sets the ISBN of the book
    )
    db.add(db_book)  # adds the new book to the session
    db.commit()  #commits to save to the database
    db.refresh(db_book)  # instance updated
    return db_book  # returns the created book

#endpoint for updating an existing book. queries by ID and updates details if found, raises 404 if not found
@app.put("/books/{book_id}", response_model=BookOut)
def update_book(book_id: int, updated_book: BookCreate, db: Session = Depends(get_db)):
    
    db_book = db.query(Book).filter(Book.id == book_id).first()  # Query the book by ID.
    if not db_book:  # if book doesn't exist, raise 404 exception
        raise HTTPException(status_code=404, detail="Book not found")
    
    db_book.title = updated_book.title  # update title
    db_book.author = updated_book.author  # Update author
    db_book.published_year = updated_book.published_year  # Update the published year
    db_book.genre = updated_book.genre  # Update the genre
    db_book.isbn = updated_book.isbn  # Update the ISBN
    
    db.commit()  # Commit session to save changes
    db.refresh(db_book)  #refresh for updated data
    return db_book  # returns the updated book

#endpoint to delete book by ID, quries by ID and deletes if exists. 404 if book doesn't exist
@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):

    db_book = db.query(Book).filter(Book.id == book_id).first()  # query by ID
    if not db_book:  # if book doesn't exist, raise 404
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(db_book)  #Delete book from session
    db.commit()  # commit session to save the delete
    return {"message": f"Book with ID {book_id} deleted"}  # retunrns successful

