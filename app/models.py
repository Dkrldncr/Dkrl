from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class UserBase(SQLModel):
    email: str = Field(index=True, unique=True)
    is_active: bool = True


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    projects: List["Project"] = Relationship(back_populates="owner")


class UserCreate(SQLModel):
    email: str
    password: str


class UserRead(SQLModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime


class ProjectBase(SQLModel):
    name: str
    description: Optional[str] = None


class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")

    owner: Optional[User] = Relationship(back_populates="projects")


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: int