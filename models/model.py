from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Enum, Table
from sqlalchemy.orm import relationship
from ..database.db_connect import Base, engine, Session
from enum import Enum as PyEnum

class Status(PyEnum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELED = "Canceled"

class Role(PyEnum):
    EXECUTIVE = "executive"
    MEMBER = "member"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    hashed_password = Column(String(255))
    is_admin = Column(Boolean, default=False)
    

    #A user can create many projects
    projects=relationship("Project", back_populates='user')
    #A user can be member of many projects
    memberships = relationship("ProjectMembership", back_populates="user")
    #A user can be assigned to many tasks
    tasks = relationship('Task', back_populates="executor")



class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    project_name = Column(String(255), unique=True, index=True)
    description = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)
    created_by = Column(Integer, ForeignKey("users.id"))

    # A project can be created by just one user
    user=relationship('User', back_populates='projects')
    # A project can have many members
    members=relationship('ProjectMembership', back_populates='project', cascade='all, delete-orphan')
    #A projects can be divided into many task
    tasks= relationship('Task', back_populates='project', cascade='all, delete-orphan')

class ProjectMembership(Base):
    __tablename__ = 'project_memberships'

    id = Column(Integer, primary_key=True)
    role = Column(Enum(Role), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))

    user = relationship("User", back_populates="memberships")
    project = relationship("Project", back_populates="members")


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    task_name = Column(String(255), unique=True, index=True)
    description = Column(String(255))
    due_date = Column(Date)
    status = Column(Enum(Status), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    executor_id  = Column(Integer, ForeignKey("users.id"))

    # Relationship: A task belongs to one project
    project = relationship('Project', back_populates='tasks')
    executor = relationship('User', back_populates='tasks')




    


Base.metadata.create_all(bind=engine)