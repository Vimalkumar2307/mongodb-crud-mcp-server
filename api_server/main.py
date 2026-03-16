"""
FastAPI REST API Server for MongoDB CRUD Operations

This is the main application file that:
1. Sets up FastAPI app
2. Defines all API endpoints
3. Handles requests and responses
4. Manages database operations

Interview Tip: When explaining this to interviewers, focus on:
- RESTful API design principles
- Async/await for performance
- Proper error handling
- Clean code organization
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
import bcrypt
from bson import ObjectId
from datetime import datetime

from .models import (
    RoleCreate, RoleUpdate, RoleInDB,
    UserCreate, UserUpdate, UserResponse,
    HealthCheck
)
from .database import (
    Database, init_database, seed_database,
    get_users_collection, get_roles_collection
)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    
    This replaces the old @app.on_event("startup") decorators.
    Benefits:
    - Cleaner syntax
    - Better resource management
    - Guaranteed cleanup on shutdown
    """
    # Startup
    await Database.connect_db()
    await init_database()
    # Optionally seed database (comment out after first run)
    # await seed_database()
    
    yield  # Application runs here
    
    # Shutdown
    await Database.close_db()


# Create FastAPI application
app = FastAPI(
    title="MongoDB CRUD API",
    description="RESTful API for User and Role management with MongoDB",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def role_name_to_id(role_identifier: str) -> ObjectId:
    """
    Convert role name to ObjectId.
    
    This allows users to specify roles by name (e.g., "admin")
    instead of MongoDB ObjectId.
    
    Args:
        role_identifier: Either a role name or ObjectId string
        
    Returns:
        ObjectId: The role's MongoDB ObjectId
        
    Raises:
        HTTPException: If role not found
    """
    # If already an ObjectId, validate and return
    if ObjectId.is_valid(role_identifier) and len(role_identifier) == 24:
        roles = await get_roles_collection()
        role = await roles.find_one({"_id": ObjectId(role_identifier)})
        if role:
            return ObjectId(role_identifier)
    
    # Otherwise, search by name
    roles = await get_roles_collection()
    role = await roles.find_one({"name": role_identifier.lower()})
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_identifier}' not found"
        )
    
    return role["_id"]


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.
    
    Why bcrypt?
    - Industry standard for password hashing
    - Includes salt automatically
    - Computationally expensive (prevents brute force)
    - Adjustable cost factor
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/", response_model=HealthCheck, tags=["Health"])
async def root():
    """
    Health check endpoint.
    
    Returns basic API information and status.
    Useful for:
    - Monitoring
    - Load balancer health checks
    - Quick API verification
    """
    return HealthCheck(
        status="healthy",
        version="2.0.0",
        database="connected",
        timestamp=datetime.utcnow()
    )


# ============================================================================
# ROLE ENDPOINTS
# ============================================================================

@app.get("/api/roles", response_model=List[RoleInDB], tags=["Roles"])
async def get_all_roles():
    """
    Get all roles from database.
    
    Returns:
        List of all roles
        
    Example Response:
        [
            {
                "_id": "507f1f77bcf86cd799439011",
                "name": "admin",
                "description": "Administrator",
                "permissions": ["read", "write", "delete", "admin"],
                "is_active": true
            }
        ]
    """
    roles_collection = await get_roles_collection()
    roles = await roles_collection.find().to_list(None)
    return roles


@app.get("/api/roles/{role_id}", response_model=RoleInDB, tags=["Roles"])
async def get_role_by_id(role_id: str):
    """
    Get a specific role by ID.
    
    Args:
        role_id: MongoDB ObjectId of the role
        
    Returns:
        Role document
        
    Raises:
        HTTPException 404: If role not found
        HTTPException 400: If invalid ObjectId format
    """
    if not ObjectId.is_valid(role_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role ID format"
        )
    
    roles_collection = await get_roles_collection()
    role = await roles_collection.find_one({"_id": ObjectId(role_id)})
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found"
        )
    
    return role


@app.post("/api/roles", response_model=RoleInDB, status_code=status.HTTP_201_CREATED, tags=["Roles"])
async def create_role(role: RoleCreate):
    """
    Create a new role.
    
    Args:
        role: Role data (name, description, permissions)
        
    Returns:
        Created role with _id
        
    Raises:
        HTTPException 400: If role name already exists
    """
    roles_collection = await get_roles_collection()
    
    # Check if role name already exists
    existing = await roles_collection.find_one({"name": role.name.lower()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{role.name}' already exists"
        )
    
    # Create role document
    role_dict = role.model_dump()
    role_dict["name"] = role_dict["name"].lower()  # Store names in lowercase
    role_dict["created_at"] = datetime.utcnow()
    role_dict["updated_at"] = datetime.utcnow()
    
    # Insert into database
    result = await roles_collection.insert_one(role_dict)
    
    # Retrieve and return created role
    created_role = await roles_collection.find_one({"_id": result.inserted_id})
    return created_role


@app.put("/api/roles/{role_id}", response_model=RoleInDB, tags=["Roles"])
async def update_role(role_id: str, role_update: RoleUpdate):
    """
    Update an existing role.
    
    Args:
        role_id: MongoDB ObjectId of role to update
        role_update: Fields to update (all optional for partial updates)
        
    Returns:
        Updated role document
        
    Raises:
        HTTPException 404: If role not found
        HTTPException 400: If invalid ObjectId or name conflict
    """
    if not ObjectId.is_valid(role_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role ID format"
        )
    
    roles_collection = await get_roles_collection()
    
    # Build update document (only include fields that were provided)
    update_data = {k: v for k, v in role_update.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # If updating name, check for duplicates
    if "name" in update_data:
        update_data["name"] = update_data["name"].lower()
        existing = await roles_collection.find_one({
            "name": update_data["name"],
            "_id": {"$ne": ObjectId(role_id)}
        })
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role name '{update_data['name']}' already exists"
            )
    
    update_data["updated_at"] = datetime.utcnow()
    
    # Update role
    result = await roles_collection.update_one(
        {"_id": ObjectId(role_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found"
        )
    
    # Return updated role
    updated_role = await roles_collection.find_one({"_id": ObjectId(role_id)})
    return updated_role


@app.delete("/api/roles/{role_id}", status_code=status.HTTP_200_OK, tags=["Roles"])
async def delete_role(role_id: str):
    """
    Delete a role.
    
    Args:
        role_id: MongoDB ObjectId of role to delete
        
    Returns:
        Success message
        
    Raises:
        HTTPException 404: If role not found
        HTTPException 400: If role is in use by users
    """
    if not ObjectId.is_valid(role_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role ID format"
        )
    
    # Check if role is in use
    users_collection = await get_users_collection()
    users_with_role = await users_collection.count_documents({"role": ObjectId(role_id)})
    
    if users_with_role > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete role. {users_with_role} user(s) have this role."
        )
    
    # Delete role
    roles_collection = await get_roles_collection()
    result = await roles_collection.delete_one({"_id": ObjectId(role_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found"
        )
    
    return {"message": "Role deleted successfully", "deleted_count": result.deleted_count}


# ============================================================================
# USER ENDPOINTS
# ============================================================================

@app.get("/api/users", response_model=List[UserResponse], tags=["Users"])
async def get_all_users():
    """
    Get all users with populated role information.
    
    Returns:
        List of users (passwords excluded for security)
    """
    users_collection = await get_users_collection()
    roles_collection = await get_roles_collection()
    
    # Get all users
    users = await users_collection.find().to_list(None)
    
    # Populate role information for each user
    for user in users:
        role_data = await roles_collection.find_one({"_id": user["role"]})
        if role_data:
            user["role"] = role_data
    
    return users


@app.get("/api/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user_by_id(user_id: str):
    """
    Get a specific user by ID with populated role.
    
    Args:
        user_id: MongoDB ObjectId of the user
        
    Returns:
        User document with role information (password excluded)
        
    Raises:
        HTTPException 404: If user not found
        HTTPException 400: If invalid ObjectId
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    users_collection = await get_users_collection()
    roles_collection = await get_roles_collection()
    
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Populate role
    role_data = await roles_collection.find_one({"_id": user["role"]})
    if role_data:
        user["role"] = role_data
    
    return user


@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def create_user(user: UserCreate):
    """
    Create a new user.
    
    Args:
        user: User data including password and role
        
    Returns:
        Created user with populated role (password excluded)
        
    Raises:
        HTTPException 400: If email exists or role not found
    """
    users_collection = await get_users_collection()
    roles_collection = await get_roles_collection()
    
    # Check if email already exists
    existing = await users_collection.find_one({"email": user.email.lower()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user.email}' already exists"
        )
    
    # Resolve role name to ID
    role_id = await role_name_to_id(user.role)
    
    # Create user document
    user_dict = user.model_dump(by_alias=True, exclude={"password"})
    user_dict["email"] = user_dict["email"].lower()
    user_dict["password_hash"] = hash_password(user.password)
    user_dict["role"] = role_id
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    
    # Insert into database
    result = await users_collection.insert_one(user_dict)
    
    # Retrieve created user with populated role
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    role_data = await roles_collection.find_one({"_id": created_user["role"]})
    created_user["role"] = role_data
    
    return created_user


@app.put("/api/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def update_user(user_id: str, user_update: UserUpdate):
    """
    Update an existing user.
    
    Args:
        user_id: MongoDB ObjectId of user to update
        user_update: Fields to update (all optional)
        
    Returns:
        Updated user with populated role
        
    Raises:
        HTTPException 404: If user not found
        HTTPException 400: If invalid ID or email conflict
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    users_collection = await get_users_collection()
    roles_collection = await get_roles_collection()
    
    # Build update document
    update_data = {k: v for k, v in user_update.model_dump(by_alias=True, exclude_unset=True).items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Handle password update
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))
    
    # Handle email update (check for duplicates)
    if "email" in update_data:
        update_data["email"] = update_data["email"].lower()
        existing = await users_collection.find_one({
            "email": update_data["email"],
            "_id": {"$ne": ObjectId(user_id)}
        })
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{update_data['email']}' already exists"
            )
    
    # Handle role update
    if "role" in update_data:
        update_data["role"] = await role_name_to_id(update_data["role"])
    
    update_data["updated_at"] = datetime.utcnow()
    
    # Update user
    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Return updated user with populated role
    updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
    role_data = await roles_collection.find_one({"_id": updated_user["role"]})
    updated_user["role"] = role_data
    
    return updated_user


@app.delete("/api/users/{user_id}", status_code=status.HTTP_200_OK, tags=["Users"])
async def delete_user(user_id: str):
    """
    Delete a user.
    
    Args:
        user_id: MongoDB ObjectId of user to delete
        
    Returns:
        Success message
        
    Raises:
        HTTPException 404: If user not found
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    users_collection = await get_users_collection()
    result = await users_collection.delete_one({"_id": ObjectId(user_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return {"message": "User deleted successfully", "deleted_count": result.deleted_count}


# ============================================================================
# SEED ENDPOINT
# ============================================================================

@app.post("/api/seed", tags=["Admin"])
async def seed_data():
    """
    Seed database with default roles and admin user.
    
    Use this endpoint to initialize the database.
    Safe to call multiple times - won't create duplicates.
    """
    await seed_database()
    return {
        "message": "Database seeded successfully",
        "admin_credentials": {
            "email": "admin@example.com",
            "password": "admin123"
        }
    }
