from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        
        # Collections
        self.users = self.db["users"]
        self.matches = self.db["matches"]
        self.sessions = self.db["sessions"]
        self.auctions = self.db["auctions"]
    
    async def get_user(self, user_id: int):
        return await self.users.find_one({"user_id": user_id})
    
    async def save_user(self, user_data: dict):
        await self.users.update_one(
            {"user_id": user_data["user_id"]},
            {"$set": user_data},
            upsert=True
        )
    
    async def create_match(self, match_data: dict):
        result = await self.matches.insert_one(match_data)
        return result.inserted_id
    
    async def get_match(self, match_id: str):
        return await self.matches.find_one({"_id": match_id})
    
    async def update_match(self, match_id: str, update_data: dict):
        await self.matches.update_one(
            {"_id": match_id},
            {"$set": update_data}
        )
    
    async def save_session(self, session_data: dict):
        await self.sessions.update_one(
            {"match_id": session_data["match_id"]},
            {"$set": session_data},
            upsert=True
        )
    
    async def get_session(self, match_id: str):
        return await self.sessions.find_one({"match_id": match_id})

db = Database()# TODO: Add your code here
