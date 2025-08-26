from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.core.db import get_session
from app.models import Project, ProjectCreate, ProjectRead, User
from .auth import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectRead])
async def list_projects(current_user: User = Depends(get_current_user), session=Depends(get_session)):
    projects = session.exec(select(Project).where(Project.owner_id == current_user.id)).all()
    return projects


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(project_in: ProjectCreate, current_user: User = Depends(get_current_user), session=Depends(get_session)):
    project = Project(**project_in.model_dump(), owner_id=current_user.id)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: int, current_user: User = Depends(get_current_user), session=Depends(get_session)):
    project = session.get(Project, project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(project_id: int, project_in: ProjectCreate, current_user: User = Depends(get_current_user), session=Depends(get_session)):
    project = session.get(Project, project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    project.name = project_in.name
    project.description = project_in.description
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, current_user: User = Depends(get_current_user), session=Depends(get_session)):
    project = session.get(Project, project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    session.delete(project)
    session.commit()
    return None