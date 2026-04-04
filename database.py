from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        
        # ========== EXISTING COLLECTIONS ==========
        self.users = self.db["users"]
        self.matches = self.db["matches"]
        self.sessions = self.db["sessions"]
        self.auctions = self.db["auctions"]
        
        # ========== NEW COLLECTIONS FOR SOLO MODE ==========
        self.solo_players = self.db["solo_players"]
        self.solo_matches = self.db["solo_matches"]
        self.solo_stats = self.db["solo_stats"]
        
        # ========== NEW COLLECTIONS FOR GAME ==========
        self.active_games = self.db["active_games"]
        self.bowling_sessions = self.db["bowling_sessions"]
        self.batting_sessions = self.db["batting_sessions"]
    
    # ==================== USER ====================
    async def get_user(self, user_id: int):
        return await self.users.find_one({"user_id": user_id})
    
    async def save_user(self, user_data: dict):
        await self.users.update_one(
            {"user_id": user_data["user_id"]},
            {"$set": user_data},
            upsert=True
        )
    
    async def update_user_state(self, user_id: int, state: str):
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"state": state, "last_active": datetime.now()}}
        )
    
    async def get_all_users(self, limit: int = 100):
        return await self.users.find().limit(limit).to_list(None)
    
    # ==================== MATCH ====================
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
    
    async def get_active_match(self, chat_id: int):
        return await self.matches.find_one({"chat_id": chat_id, "status": "live"})
    
    # ==================== SESSION ====================
    async def save_session(self, session_data: dict):
        await self.sessions.update_one(
            {"match_id": session_data["match_id"]},
            {"$set": session_data},
            upsert=True
        )
    
    async def get_session(self, match_id: str):
        return await self.sessions.find_one({"match_id": match_id})
    
    async def delete_session(self, match_id: str):
        await self.sessions.delete_one({"match_id": match_id})
    
    # ==================== ACTIVE GAMES ====================
    async def save_active_game(self, chat_id: int, game_data: dict):
        await self.active_games.update_one(
            {"chat_id": chat_id},
            {"$set": game_data},
            upsert=True
        )
    
    async def get_active_game(self, chat_id: int):
        return await self.active_games.find_one({"chat_id": chat_id})
    
    async def delete_active_game(self, chat_id: int):
        await self.active_games.delete_one({"chat_id": chat_id})
    
    # ==================== SOLO MODE ====================
    async def get_solo_player(self, user_id: int):
        return await self.solo_players.find_one({"user_id": user_id})
    
    async def save_solo_player(self, player_data: dict):
        await self.solo_players.update_one(
            {"user_id": player_data["user_id"]},
            {"$set": player_data},
            upsert=True
        )
    
    async def update_solo_player_stats(self, user_id: int, runs: int, balls: int, fours: int, sixes: int, is_wicket: bool):
        player = await self.get_solo_player(user_id)
        if player:
            new_runs = player.get("total_runs", 0) + runs
            new_balls = player.get("total_balls", 0) + balls
            new_fours = player.get("total_fours", 0) + fours
            new_sixes = player.get("total_sixes", 0) + sixes
            new_matches = player.get("total_matches", 0) + (1 if is_wicket else 0)
            
            await self.solo_players.update_one(
                {"user_id": user_id},
                {"$set": {
                    "total_runs": new_runs,
                    "total_balls": new_balls,
                    "total_fours": new_fours,
                    "total_sixes": new_sixes,
                    "total_matches": new_matches,
                    "last_active": datetime.now()
                }}
            )
    
    async def get_all_solo_players(self, limit: int = 50):
        return await self.solo_players.find().sort("total_runs", -1).limit(limit).to_list(None)
    
    async def save_solo_match(self, match_data: dict):
        await self.solo_matches.insert_one(match_data)
    
    async def get_solo_match_history(self, user_id: int, limit: int = 10):
        return await self.solo_matches.find({"user_id": user_id}).sort("created_at", -1).limit(limit).to_list(None)
    
    # ==================== BOWLING SESSIONS ====================
    async def save_bowling_session(self, match_id: str, session_data: dict):
        await self.bowling_sessions.update_one(
            {"match_id": match_id},
            {"$set": session_data},
            upsert=True
        )
    
    async def get_bowling_session(self, match_id: str):
        return await self.bowling_sessions.find_one({"match_id": match_id})
    
    async def delete_bowling_session(self, match_id: str):
        await self.bowling_sessions.delete_one({"match_id": match_id})
    
    # ==================== BATTING SESSIONS ====================
    async def save_batting_session(self, match_id: str, session_data: dict):
        await self.batting_sessions.update_one(
            {"match_id": match_id},
            {"$set": session_data},
            upsert=True
        )
    
    async def get_batting_session(self, match_id: str):
        return await self.batting_sessions.find_one({"match_id": match_id})
    
    async def delete_batting_session(self, match_id: str):
        await self.batting_sessions.delete_one({"match_id": match_id})
    
    # ==================== AUCTION ====================
    async def create_auction(self, auction_data: dict):
        result = await self.auctions.insert_one(auction_data)
        return result.inserted_id
    
    async def get_auction(self, auction_id: str):
        return await self.auctions.find_one({"auction_id": auction_id})
    
    async def update_auction(self, auction_id: str, update_data: dict):
        await self.auctions.update_one(
            {"auction_id": auction_id},
            {"$set": update_data}
        )
    
    # ==================== UTILITY ====================
    async def ping(self):
        """Check database connection"""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            return False
    
    async def create_indexes(self):
        """Create indexes for better performance"""
        await self.users.create_index("user_id", unique=True)
        await self.users.create_index("last_active")
        
        await self.matches.create_index("match_id", unique=True)
        await self.matches.create_index("status")
        
        await self.sessions.create_index("match_id", unique=True)
        await self.sessions.create_index("last_update")
        
        await self.solo_players.create_index("user_id", unique=True)
        await self.solo_players.create_index("total_runs", -1)
        
        await self.active_games.create_index("chat_id", unique=True)
        await self.active_games.create_index("expires_at")

# Import datetime for timestamp
from datetime import datetime

# Create database instance
db = Database()
