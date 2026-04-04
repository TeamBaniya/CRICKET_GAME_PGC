# TODO: Add your code here
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class UserStats(BaseModel):
    """User cricket statistics"""
    total_matches: int = 0
    wins: int = 0
    losses: int = 0
    ties: int = 0
    total_runs: int = 0
    total_wickets: int = 0
    highest_score: int = 0
    best_bowling: str = "0/0"
    catches: int = 0
    stumpings: int = 0
    
    @property
    def win_rate(self) -> float:
        if self.total_matches == 0:
            return 0.0
        return (self.wins / self.total_matches) * 100
    
    @property
    def batting_average(self) -> float:
        if self.total_matches == 0:
            return 0.0
        return self.total_runs / self.total_matches

class User(BaseModel):
    """User model for database"""
    user_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    
    # User metadata
    joined_date: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    is_admin: bool = False
    is_banned: bool = False
    
    # User preferences
    language: str = "en"
    notifications: bool = True
    
    # Game stats
    stats: UserStats = Field(default_factory=UserStats)
    
    # Current game state
    current_match_id: Optional[str] = None
    current_state: str = "main_menu"
    
    # Wallet/Auction
    coins: int = 1000  # Starting coins for auction
    team_players: List[str] = Field(default_factory=list)
    
    def update_last_active(self):
        """Update last active timestamp"""
        self.last_active = datetime.now()
    
    def add_match_result(self, won: bool, runs: int, wickets: int):
        """Update user stats after match"""
        self.stats.total_matches += 1
        self.stats.total_runs += runs
        self.stats.total_wickets += wickets
        
        if runs > self.stats.highest_score:
            self.stats.highest_score = runs
        
        if won:
            self.stats.wins += 1
        else:
            self.stats.losses += 1
    
    def deduct_coins(self, amount: int) -> bool:
        """Deduct coins from user wallet"""
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False
    
    def add_coins(self, amount: int):
        """Add coins to user wallet"""
        self.coins += amount
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create User from dictionary"""
        return cls(**data)

# MongoDB schema reference
UserSchema = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "first_name"],
            "properties": {
                "user_id": {"bsonType": "int"},
                "username": {"bsonType": "string"},
                "first_name": {"bsonType": "string"},
                "last_name": {"bsonType": "string"},
                "joined_date": {"bsonType": "date"},
                "last_active": {"bsonType": "date"},
                "is_active": {"bsonType": "bool"},
                "is_admin": {"bsonType": "bool"},
                "is_banned": {"bsonType": "bool"},
                "coins": {"bsonType": "int"},
                "stats": {
                    "bsonType": "object",
                    "properties": {
                        "total_matches": {"bsonType": "int"},
                        "wins": {"bsonType": "int"},
                        "losses": {"bsonType": "int"},
                        "total_runs": {"bsonType": "int"},
                        "total_wickets": {"bsonType": "int"},
                        "highest_score": {"bsonType": "int"}
                    }
                }
            }
        }
    }
}
