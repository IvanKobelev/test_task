"""Pydantic schemas."""

from pydantic import BaseModel, validator

from src.enums import UserRole


class BasicOut(BaseModel):
    """Basic successfull response schema."""

    message: str


class ErrorOut(BaseModel):
    """Basic error response schema."""

    detail: str


class CreateUserIn(BaseModel):
    """Create user request schema."""

    email: str
    first_name: str
    password: str
    second_name: str


class UpdateUserIn(BaseModel):
    """Update user request schema."""

    first_name: str | None
    second_name: str | None


class TokenData(BaseModel):
    """Token data schema."""

    id: int
    role: UserRole

    @validator("role")
    def return_enum_values(cls, field: UserRole) -> str:
        """Return value for enum field."""
        return field.value

    class Config:
        """Schema configuration."""

        orm_mode = True


class QueueMessage(BaseModel):
    """Schema for rabbitmq service queue."""

    email: str
    message: str


class UserOut(BaseModel):
    """User response schema."""

    id: int
    email: str
    first_name: str
    role: UserRole
    second_name: str

    @validator("role")
    def return_enum_values(cls, field: UserRole) -> str:
        """Return value for enum field."""
        return field.value

    class Config:
        """Schema configuration."""

        orm_mode = True


class LoginUserIn(BaseModel):
    """Login user request schema."""

    email: str
    password: str


class LoginUserOut(BaseModel):
    """Login user response schema."""

    token: str
    user: UserOut
