from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr | None = None
    full_name: str
    role: UserRole

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    email: EmailStr | None = None
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.student
