from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from utils import templates, serializer, auth
from database.db_connect import Session
from models.model import User, Project, ProjectMembership, Role, Status
from typing import Annotated
from datetime import date
from sqlalchemy.exc import SQLAlchemyError

project_router = APIRouter(
    prefix="/project", 
    tags=["Tasks Routes"]
)