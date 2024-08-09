from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from ..utils import templates, serializer, auth
from ..database.db_connect import Session
from ..models.model import User, Project, ProjectMembership, Role, Status
from typing import Annotated
from datetime import date
from sqlalchemy.exc import SQLAlchemyError

project_router = APIRouter(
    prefix="/project"
)

## Project route
@project_router.post("/")
def create_project(request: Request, project_name:Annotated[str, Form()], description:Annotated[str, Form()]):
    if request.state.custom_data["current_userId"]:
        id = request.state.custom_data["current_userId"]
        try:
            session = Session()
            user = session.query(User).filter(User.id==id).one()
            project = Project(project_name=project_name,
                            description=description,
                            start_date=date(2024, 11, 15),
                            end_date=date(2025, 2, 6),
                            user=user)
            member = ProjectMembership(role="executive",user=user, project=project)
            session.add(project)
            session.add(member)
            session.commit()
            session.close()
            return JSONResponse(content={
                'message': "Project created"
            }, status_code=201)
        except SQLAlchemyError as e:
            session.close()
            return JSONResponse(content={
                'message': str(e)
            })
        except Exception as e:
            return JSONResponse(content={
                'message': str(e)
            })
    else:
        return JSONResponse(content={
                'message': "Unauthorized user"
            })
    

@project_router.delete("/{project_id}")
def delete_project(project_id: int, request: Request):
#     project_id_to_filter = 1  # Replace with the actual project ID
# role_to_filter = Role.MANAGER  # Replace with the actual Role Enum member
    try:
        #user_id = request.state.custom_data["current_userId"]
#         memberships = session.query(ProjectMembership).filter(
#     ProjectMembership.project_id == project_id_to_filter,
#     ProjectMembership.role == role_to_filter
# ).all()
        session = Session()
        project = session.query(Project).get(project_id)
        print(project)
        
        if project:
            session.query(Project).get(project_id)
            session.delete(project)
            
        else:
            return JSONResponse(content={
                    'message': "Unauthorized user"
                })
    except SQLAlchemyError as e:
        return JSONResponse(content={
                    'message': str(e)
                })
    except Exception as e:
        return JSONResponse(content={
                    'message': str(e)
                })