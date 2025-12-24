import asyncpg
import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import json

load_dotenv()

class NeonDBService:
    """
    Service for interacting with Neon PostgreSQL database.
    """
    
    def __init__(self):
        self.database_url = os.getenv("NEON_DATABASE_URL")
        if not self.database_url:
            print("Warning: NEON_DATABASE_URL not set. Database functionality will be limited.")
            self.database_url = None
        self.pool = None
    
    async def connect(self):
        """
        Create a connection pool to the Neon database.
        """
        if not self.database_url:
            return False
        
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            print("Connected to Neon database successfully")
            return True
        except Exception as e:
            print(f"Error connecting to Neon database: {e}")
            return False
    
    async def create_tables(self):
        """
        Create necessary tables in the database.
        """
        if not self.pool:
            return False
        
        # Create users table
        await self.pool.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create chat_history table
        await self.pool.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                source_documents TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create content_ingestion_log table
        await self.pool.execute("""
            CREATE TABLE IF NOT EXISTS content_ingestion_log (
                id SERIAL PRIMARY KEY,
                chapter_id VARCHAR(100) NOT NULL,
                content_preview TEXT,
                ingestion_status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("Database tables created successfully")
        return True
    
    async def add_user(self, username: str, email: str) -> Optional[int]:
        """
        Add a new user to the database.
        """
        if not self.pool:
            return None
        
        try:
            user_id = await self.pool.fetchval(
                "INSERT INTO users (username, email) VALUES ($1, $2) RETURNING id",
                username, email
            )
            return user_id
        except Exception as e:
            print(f"Error adding user: {e}")
            return None
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user details by ID.
        """
        if not self.pool:
            return None
        
        try:
            row = await self.pool.fetchrow(
                "SELECT id, username, email, created_at FROM users WHERE id = $1",
                user_id
            )
            if row:
                return {
                    "id": row["id"],
                    "username": row["username"],
                    "email": row["email"],
                    "created_at": row["created_at"]
                }
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    async def save_chat_history(self, user_id: int, question: str, answer: str, source_documents: List[str] = None) -> Optional[int]:
        """
        Save chat history to the database.
        """
        if not self.pool:
            return None
        
        try:
            source_docs_str = json.dumps(source_documents) if source_documents else "[]"
            chat_id = await self.pool.fetchval(
                "INSERT INTO chat_history (user_id, question, answer, source_documents) VALUES ($1, $2, $3, $4) RETURNING id",
                user_id, question, answer, source_docs_str
            )
            return chat_id
        except Exception as e:
            print(f"Error saving chat history: {e}")
            return None
    
    async def get_chat_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get chat history for a user.
        """
        if not self.pool:
            return []
        
        try:
            rows = await self.pool.fetch(
                """
                SELECT id, question, answer, source_documents, created_at 
                FROM chat_history 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2
                """,
                user_id, limit
            )
            
            history = []
            for row in rows:
                history.append({
                    "id": row["id"],
                    "question": row["question"],
                    "answer": row["answer"],
                    "source_documents": json.loads(row["source_documents"]) if row["source_documents"] else [],
                    "created_at": row["created_at"]
                })
            
            return history
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []
    
    async def log_content_ingestion(self, chapter_id: str, content_preview: str, status: str = "completed"):
        """
        Log content ingestion to the database.
        """
        if not self.pool:
            return False
        
        try:
            await self.pool.execute(
                "INSERT INTO content_ingestion_log (chapter_id, content_preview, ingestion_status) VALUES ($1, $2, $3)",
                chapter_id, content_preview[:500], status  # Limit preview to 500 chars
            )
            return True
        except Exception as e:
            print(f"Error logging content ingestion: {e}")
            return False
    
    async def close(self):
        """
        Close the database connection pool.
        """
        if self.pool:
            await self.pool.close()