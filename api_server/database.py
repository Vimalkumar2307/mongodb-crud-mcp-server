"""
Database Configuration and Connection Management

This module handles:
- MongoDB connection using Motor (async MongoDB driver)
- Database initialization
- Connection lifecycle management

Why Motor instead of PyMongo?
- Motor is async/await compatible
- FastAPI is async by default
- Better performance for concurrent requests
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """
    Database connection manager using Singleton pattern.
    
    Singleton Pattern: Ensures only one database connection exists.
    Benefits:
    - Resource efficiency (one connection pool)
    - Consistent state across application
    - Easy to manage connection lifecycle
    """
    
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None
    
    @classmethod
    async def connect_db(cls):
        """
        Establish connection to MongoDB Atlas.
        
        This is called when the FastAPI application starts.
        Connection pooling is handled automatically by Motor.
        """
        try:
            mongodb_uri = os.getenv("MONGODB_URI")
            if not mongodb_uri:
                raise ValueError("MONGODB_URI not found in environment variables")
            
            # Create async MongoDB client
            cls.client = AsyncIOMotorClient(mongodb_uri)
            
            # Get database (database name is in the connection string)
            # Extract database name from URI or use default
            db_name = "crud_app_db"
            cls.database = cls.client[db_name]
            
            # Test connection with a ping
            await cls.client.admin.command('ping')
            
            logger.info(f"✅ Successfully connected to MongoDB database: {db_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            raise
    
    @classmethod
    async def close_db(cls):
        """
        Close database connection gracefully.
        
        This is called when the FastAPI application shuts down.
        Important for cleanup and releasing resources.
        """
        if cls.client:
            cls.client.close()
            logger.info("✅ MongoDB connection closed")
    
    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """
        Get the database instance.
        
        Returns:
            AsyncIOMotorDatabase: The MongoDB database instance
            
        Raises:
            RuntimeError: If database is not connected
        """
        if cls.database is None:
            raise RuntimeError("Database not connected. Call connect_db() first.")
        return cls.database
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """
        Get a specific collection from the database.
        
        Args:
            collection_name: Name of the collection (e.g., 'users', 'roles')
            
        Returns:
            AsyncIOMotorCollection: MongoDB collection instance
        """
        db = cls.get_database()
        return db[collection_name]


# Convenience functions for accessing collections
async def get_users_collection():
    """Get the 'users' collection"""
    return Database.get_collection("users")


async def get_roles_collection():
    """Get the 'roles' collection"""
    return Database.get_collection("roles")


# Database initialization for creating indexes
async def init_database():
    """
    Initialize database with indexes and constraints.
    
    Indexes improve query performance significantly.
    For example:
    - Email lookup: O(1) with index vs O(n) without
    - Unique constraints prevent duplicates
    """
    try:
        db = Database.get_database()
        
        # Create indexes for users collection
        users = db["users"]
        await users.create_index("email", unique=True)  # Email must be unique
        await users.create_index("role")  # Faster lookups by role
        await users.create_index("is_active")  # Filter active users quickly
        
        # Create indexes for roles collection
        roles = db["roles"]
        await roles.create_index("name", unique=True)  # Role name must be unique
        await roles.create_index("is_active")
        
        logger.info("✅ Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {str(e)}")
        raise


# Seed data for initial setup
async def seed_database():
    """
    Populate database with default roles and admin user.
    
    This is helpful for:
    - First-time setup
    - Development/testing
    - Ensuring critical roles exist
    """
    try:
        db = Database.get_database()
        roles_collection = db["roles"]
        users_collection = db["users"]
        
        # Check if roles already exist
        existing_roles_count = await roles_collection.count_documents({})
        if existing_roles_count > 0:
            logger.info("⚠️ Database already seeded, skipping...")
            return
        
        # Create default roles
        default_roles = [
            {
                "name": "admin",
                "description": "Administrator with full access",
                "permissions": ["read", "write", "delete", "admin"],
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "name": "user",
                "description": "Regular user with limited access",
                "permissions": ["read"],
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "name": "manager",
                "description": "Manager with read and write access",
                "permissions": ["read", "write"],
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "name": "editor",
                "description": "Editor with content management access",
                "permissions": ["read", "write"],
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Insert roles
        result = await roles_collection.insert_many(default_roles)
        admin_role_id = result.inserted_ids[0]
        
        # Create default admin user
        import bcrypt
        from datetime import datetime
        
        hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
        
        admin_user = {
            "first_name": "Admin",
            "last_name": "User",
            "email": "admin@example.com",
            "password_hash": hashed_password.decode('utf-8'),
            "phone": "+1234567890",
            "date_of_birth": None,
            "role": admin_role_id,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await users_collection.insert_one(admin_user)
        
        logger.info("✅ Database seeded with default roles and admin user")
        logger.info("📧 Default admin login: admin@example.com / admin123")
        
    except Exception as e:
        logger.error(f"❌ Failed to seed database: {str(e)}")
        raise
