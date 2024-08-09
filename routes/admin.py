from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from pydantic import EmailStr, BaseModel
from utils import templates, serializer, auth
from database.db_connect import Session
from models.model import User
from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError

admin_router = APIRouter(
    prefix="/admin"
)

class User(BaseModel):
    first_name: str
    last_name:str
    email: EmailStr
    password: str
    is_admin: bool = False


#user Routes for admin
@admin_router.get("/user/{user_id}")
def get_user(user_id: int):
    session = Session()
    result = session.query(User).filter(User.id == user_id).one()
    try:
        result = session.query(User).filter(User.id == user_id).one()
        session.close()
        return JSONResponse(content={"user":result}, status_code=200)
    except SQLAlchemyError as e:
        session.close()
        return  JSONResponse(content={
            "message": str(e)
        }) 
    except Exception as e:
        session.close()
        return  JSONResponse(content={
            "message": str(e)
        }) 
    
    
@admin_router.get("/user")
def get_users():
    session = Session()
    users = []
    try:
        results = session.query(User).all()
        if results:
            for result in results:
                users.append(result)
            session.close()
            return {"users": users}
        else:
            session.close()
            return "No users"
    except SQLAlchemyError as e:
        session.close()
        return  JSONResponse(content={
            "message": str(e)
        }) 
    except Exception as e:
        session.close()
        return  JSONResponse(content={
            "message": str(e)
        }) 

@admin_router.post("/user")
def create_user(first_name: Annotated[str, Form()], last_name: Annotated[str, Form()], 
                email: Annotated[EmailStr, Form()], password:Annotated[str, Form()],
                is_admin:Annotated[bool, Form()]=False):
    hashed_password = auth.hash_password(password)
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        hashed_password = hashed_password,
        is_admin = is_admin
    )
    try:
        session=Session()
        session.add(new_user)
        session.commit()
        session.close()
        return JSONResponse(content={"message":"User created"}, status_code=201)
    except SQLAlchemyError as e:
        session.close()
        return  JSONResponse(content={
            "message": str(e)
        }) 
    except Exception as e:
        session.close()
        return  JSONResponse(content={
            "message": str(e)
        }) 


@admin_router.put("/user/{user_id}")
def update_user(user_id: int, first_name: Annotated[str, Form()], last_name: Annotated[str, Form()],
                is_admin:Annotated[bool, Form()]):
    try:
        session = Session()
        result = session.query(User).filter(User.id == user_id).one()
        if result:
            if first_name:
                result.update({User.first_name: first_name})
            if last_name:
                result.update({User.last_name: last_name})
            if is_admin:
                result.update({User.is_admin: is_admin})
            session.commit()
            session.close()
            return JSONResponse(content={"message": "Task updated"})
    except SQLAlchemyError as e:
        session.close()
        if str(e) == "No row was found when one was required":
            return JSONResponse(content={
                "message": "User does not exists"
            })
        return JSONResponse(content={
                "message": str(e)
        })
    except Exception as e:
        return JSONResponse(content={
                "message": str(e)
        })


@admin_router.delete("/user/{user_id}")
def delete_user(user_id: int):
    try:
        session = Session()
        result = session.query(User).filter(User.id==user_id).one()
        if result:
            session.query(User).filter(User.id==user_id).delete()
            session.commit()
            session.close()
            return JSONResponse(content={"message":"User deleted"}, status_code=210)
    except SQLAlchemyError as e:
        session.close()
        if str(e) == "No row was found when one was required":
            return JSONResponse(content={
                "message": "User does not exists"
            })
        return JSONResponse(content={
                "message": str(e)
        })
    except Exception as e:
        session.close()
        return  JSONResponse(content={
            "message": str(e)
        }, status_code=501) 