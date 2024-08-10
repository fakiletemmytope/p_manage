from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from utils import templates, serializer, auth
from database.db_connect import Session
from models.model import User, Project, ProjectMembership, Role, Status
from typing import Annotated
from datetime import date
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

project_router = APIRouter(
    prefix="/project", 
    tags=["Projects Routes"]
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
            member = ProjectMembership(role=Role.EXECUTIVE,user=user, project=project)
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
        try:
            session=Session()
            current_user_id = request.state.custom_data['current_userId']
            memberRole = session.query(ProjectMembership).filter(ProjectMembership.project_id==project_id, ProjectMembership.user_id==current_user_id, ProjectMembership.role=="executive").one_or_none       
            if memberRole is None:
                return JSONResponse(content={
                        'message': 'Unauthorised User'
                    }, status_code=200)            
            project = session.query(Project).filter(Project.id == project_id).one_or_none()
            if memberRole or request.state.custom_data["current_userRole"] == "admin":
                if project == None:
                    return JSONResponse(content={
                            'message': 'Project is not found'
                        }, status_code=403)
                else:
                    session.delete(project)
                    session.commit()
                    session.close()
                    return JSONResponse(content={
                            'message': 'Project deleted'
                        }, status_code=210)
        except SQLAlchemyError as e:
            return JSONResponse(content={
                        'message': str(e)
                    }, status_code=500)
        except Exception as e:
            return JSONResponse(content={
                        'message': str(e)
                    }, status_code=500)
    
@project_router.put("/{project_id}")
def update_project(project_id: int, request: Request, project_name:Annotated[str, Form()]=None, description:Annotated[str, Form()] = None):
    try:            
        session=Session()
        current_user_id = request.state.custom_data['current_userId']
        memberRole = session.query(ProjectMembership).filter(ProjectMembership.project_id==project_id, ProjectMembership.user_id==current_user_id, ProjectMembership.role=="executive").one_or_none()      
        if memberRole is None:
            return JSONResponse(content={
                    'message': 'Unauthorised User'
                }, status_code=200)            
        project = session.query(Project).filter(Project.id == project_id).one_or_none()
        if memberRole or request.state.custom_data["current_userRole"] == "admin":
            if project == None:
                return JSONResponse(content={
                        'message': 'Project is not found'
                    }, status_code=403)
            else:
                if project_name:
                    project = session.query(Project).filter(Project.id == project_id).update({Project.project_name:project_name})
                if description:
                    project = session.query(Project).filter(Project.id == project_id).update({Project.description:description})
                session.commit()
                session.close()
                return JSONResponse(content={
                        'message': 'Project updated'
                    }, status_code=210)
    except SQLAlchemyError as e:
            return JSONResponse(content={
                        'message': str(e)
                    }, status_code=500)
    except Exception as e:
            return JSONResponse(content={
                        'message': str(e)
                    }, status_code=500)

@project_router.get("/{project_id}")
async def get_project(request: Request, project_id: int):
    try:            
        session=Session()
        current_user_id = request.state.custom_data['current_userId']
        memberRole = session.query(ProjectMembership).filter(ProjectMembership.project_id==project_id, ProjectMembership.user_id==current_user_id).one_or_none       
        if memberRole is None:
            return JSONResponse(content={
                    'message': 'Unauthorised User'
                }, status_code=200)            
        project = session.query(Project).filter(Project.id == project_id).one_or_none()
        if memberRole or request.state.custom_data["current_userRole"] == "admin":
            if project == None:
                return JSONResponse(content={
                        'message': 'Project is not found'
                    }, status_code=403)
            else:
                params =["id", "project_name", "description"]
                result = await serializer.serialize(params, project)   
                session.commit()
                session.close()
                return JSONResponse(content={
                        'project':result
                    }, status_code=210)
    except SQLAlchemyError as e:
            return JSONResponse(content={
                        'message': str(e)
                    }, status_code=500)
    except Exception as e:
            return JSONResponse(content={
                        'message': str(e)
                    }, status_code=500)

@project_router.get("/")
async def get_projects(request: Request):
    try:            
        # Query the ProjectMembership table to get project_ids for the given user_id
        if request.state.custom_data["current_userRole"] == "admin":
             session = Session()
             projects = session.query(Project).all()
        else:
            user_id = request.state.custom_data["current_userId"]
            subquery = select(ProjectMembership.project_id).filter(ProjectMembership.user_id == user_id).subquery()
            # Use the subquery to filter the projects table
            session = Session()
            result = session.execute(select(Project).filter(Project.id.in_(subquery)))
            projects = result.scalars().all()
        params = ["id", "project_name", "description"]
        data = []
        for project in projects:
                serialized = await serializer.serialize(params, project)
                print("Serialized:", serialized)
                data.append(serialized)
        return JSONResponse(content={
             'projects':data
        })
    except SQLAlchemyError as e:
            return JSONResponse(content={
                        'message': str(e)
                    }, status_code=500)
    except Exception as e:
            return JSONResponse(content={
                        'message': str(e)
                    }, status_code=500)