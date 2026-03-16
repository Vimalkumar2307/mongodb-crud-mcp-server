"""
Database Models for MongoDB Collections

This module defines Pydantic models that represent our MongoDB documents.
Pydantic provides:
- Automatic validation
- Type hints
- JSON serialization
- Documentation generation
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId


# Custom type for MongoDB ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ])
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")


# Role Models
class RoleBase(BaseModel):
    """
    Base Role model - fields that are common to all role operations.
    
    Why separate Base/Create/Update models?
    - DRY principle (Don't Repeat Yourself)
    - Different operations need different field requirements
    - Better validation control
    """
    name: str = Field(..., min_length=1, max_length=50, description="Role name")
    description: str = Field(..., min_length=1, max_length=200)
    permissions: List[str] = Field(
        default_factory=list,
        description="List of permissions: read, write, delete, admin"
    )
    is_active: bool = Field(default=True, description="Whether role is active")


class RoleCreate(RoleBase):
    """Model for creating a new role - inherits all fields from RoleBase"""
    pass


class RoleUpdate(BaseModel):
    """
    Model for updating a role - all fields are optional.
    
    Why all optional? 
    - PATCH operation allows partial updates
    - Client can update just one field without sending all fields
    """
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class RoleInDB(RoleBase):
    """
    Model representing a role as stored in MongoDB.
    
    Additional fields:
    - id: MongoDB's _id field (we alias it to 'id' for cleaner API)
    - created_at: Timestamp when role was created
    - updated_at: Timestamp when role was last updated
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        # Allow field aliasing (_id -> id)
        populate_by_name = True
        # Allow arbitrary types (like PyObjectId)
        arbitrary_types_allowed = True
        # JSON schema customization
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}
        # Example for API documentation
        json_schema_extra = {
            "example": {
                "name": "admin",
                "description": "Administrator with full access",
                "permissions": ["read", "write", "delete", "admin"],
                "is_active": True
            }
        }


# User Models
class UserBase(BaseModel):
    """Base User model with common fields"""
    first_name: str = Field(..., min_length=1, max_length=50, alias="firstName")
    last_name: str = Field(..., min_length=1, max_length=50, alias="lastName")
    email: EmailStr = Field(..., description="Valid email address")
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[datetime] = Field(None, alias="dateOfBirth")
    is_active: bool = Field(default=True, alias="isActive")

    class Config:
        populate_by_name = True


class UserCreate(UserBase):
    """
    Model for creating a new user.
    
    Additional required fields:
    - password: Required for new users
    - role: Reference to a Role document
    """
    password: str = Field(..., min_length=6, description="Minimum 6 characters")
    role: str = Field(..., description="Role ID or role name")


class UserUpdate(BaseModel):
    """Model for updating user - all fields optional for partial updates"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, alias="firstName")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, alias="lastName")
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[datetime] = Field(None, alias="dateOfBirth")
    role: Optional[str] = None
    is_active: Optional[bool] = Field(None, alias="isActive")

    class Config:
        populate_by_name = True


class UserInDB(UserBase):
    """
    Model representing a user as stored in MongoDB.
    
    Note: password is hashed, not plain text.
    The 'role' field can be either:
    - PyObjectId (reference to Role)
    - RoleInDB (populated role document)
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    password_hash: str = Field(..., description="Bcrypt hashed password")
    role: PyObjectId | RoleInDB = Field(..., description="Role reference or populated role")
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}
        json_schema_extra = {
            "example": {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "role": "admin",
                "isActive": True
            }
        }


class UserResponse(UserBase):
    """
    Model for user responses - excludes password_hash for security.
    
    This is what gets sent to clients - never expose password hashes!
    """
    id: PyObjectId = Field(..., alias="_id")
    role: RoleInDB  # Always return populated role in responses
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


# Health Check Model
class HealthCheck(BaseModel):
    """Model for API health check endpoint"""
    status: str = "healthy"
    version: str = "2.0.0"
    database: str = "connected"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
