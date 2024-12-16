from fastapi import Depends, FastAPI, HTTPException  # Import FastAPI and related modules.
from pydantic import BaseModel, EmailStr  # Import Pydantic BaseModel and Email validation type.
from typing import List  # Import List for type hinting.
from sqlalchemy import create_engine, Column, Integer, String  # SQLAlchemy utilities for ORM mapping.
from sqlalchemy.ext.declarative import declarative_base  # Base class for SQLAlchemy models.
from sqlalchemy.orm import sessionmaker, Session  # Session and sessionmaker for database operations.