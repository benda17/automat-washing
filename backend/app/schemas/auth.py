from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("username", mode="before")
    @classmethod
    def strip_username(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("password", mode="before")
    @classmethod
    def strip_password(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
