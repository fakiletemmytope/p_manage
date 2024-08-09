from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from pydantic import EmailStr, BaseModel
from ..utils import templates, serializer, auth
from ..database.db_connect import Session
from ..models.model import User, Project, ProjectMembership
from typing import Annotated
from datetime import date
from sqlalchemy.exc import SQLAlchemyError

user_router = APIRouter(
    prefix="/user"
)


# class User(BaseModel):
#     first_name: str
#     last_name:str
#     email: EmailStr
#     password: str
#     is_admin: bool = False

#user Routes for all users

#user login
@user_router.post('/login')
async def login(email: Annotated[EmailStr, Form()], password: Annotated[str, Form()]):
     
    try:
        session = Session()   
        user = session.query(User).filter(User.email == email).first()
        # print(user.__dict__)
        if auth.password_verification(password, user.hashed_password):
            payload={
                'current_user_name': f'{user.first_name} {user.last_name}',
                'current_user_is_admin': user.is_admin,
                'current_user_id':  user.id
            }

            token = auth.get_token(payload)
            return JSONResponse(content={
                'message':"User logged in",
                'token': token
            }, status_code=200)
        else:
            return JSONResponse(content={'message':"Incorrect password"}, status_code=403)
    except SQLAlchemyError as e:
        return JSONResponse(content={'message': str(e)})
    except Exception as e:
        return JSONResponse(content={'message': str(e)})

#user get their details
@user_router.get("/{user_id}")
def get_user(request: Request, user_id: int):
    session = Session()
    result = session.query(User).filter(User.id == user_id).one().__dict__
    print(result)
    
    if user_id == request.state.custom_data["current_userId"]:
        try:
            result = session.query(User).filter(User.id == user_id).one()
            session.close()
            user_details={
                "first_name": result.first_name,
                "last_name": result.last_name,
                'email': result.email
            }
            return JSONResponse(content={"user":user_details}, status_code=200)
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
    else:
        return JSONResponse(content={
            'message':'unauthorized action'
        })

#user registration
@user_router.post("/")
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

#user update their details(first and last name only)
@user_router.put("/{user_id}")
def update_user(user_id: int, request: Request, first_name: Annotated[str, Form()]=None, last_name: Annotated[str, Form()]=None,
                ):
    if user_id == request.state.custom_data["current_userId"]:
        try:
            session = Session()
            result = session.query(User).filter(User.id == user_id).one()
            if result:
                if first_name:
                    session.query(User).filter(User.id == user_id).update({User.first_name: first_name})
                if last_name:
                    session.query(User).filter(User.id == user_id).update({User.last_name: last_name})
                session.commit()
                session.close()
                return JSONResponse(content={"message": "user details updated"})
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
    else:
        return JSONResponse(content={
            'message':'unauthorized action'
        })
        
#user delete accout
@user_router.delete("/{user_id}")
def delete_user(request: Request, user_id: int):
    if user_id == request.state.custom_data["current_userId"]:
        try:
            session = Session()
            result = session.query(User).filter(User.id==user_id).one()
            if result:
                result.delete()
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
    else:
        return JSONResponse(content={
            'message':'unauthorized action'
        })
    




