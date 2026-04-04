# TODO: Add your code here
from datetime import datetime
from typing import Optional, List, Dict, Literal
from pydantic import BaseModel, Field

AuctionStatus = Literal["waiting", "live", "paused", "completed"]
PlayerStatus = Literal["available", "sold", "unsold", "hold"]

class AuctionPlayer(BaseModel):
    """Auction player model"""
    player_id: str
    name: str
    base_price: int
    current_bid: int = 0
    current_bidder: Optional[int] = None
    status: PlayerStatus = "available"
    category: Literal["batsman", "bowler", "all_rounder", "wicket_keeper"] = "batsman"
    rating: int = 50  # 1-100
    
    def place_bid(self, bidder_id: int, amount: int) -> bool:
        """Place a bid on player"""
        if amount > self.current_bid and amount >= self.base_price:
            self.current_bid = amount
            self.current_bidder = bidder_id
            return True
        return False
    
    def sell(self):
        """Mark player as sold"""
        self.status = "sold"
    
    def unsold(self):
        """Mark player as unsold"""
        self.status = "unsold"
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return self.model_dump()

class Auction(BaseModel):
    """Auction model"""
    auction_id: str
    title: str
    host_id: int
    status: AuctionStatus = "waiting"
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Players
    players: List[AuctionPlayer] = Field(default_factory=list)
    sold_players: List[AuctionPlayer] = Field(default_factory=list)
    unsold_players: List[AuctionPlayer] = Field(default_factory=list)
    
    # Participants
    participants: List[Dict] = Field(default_factory=list)  # [{user_id, username, coins}]
    
    # Current state
    current_player_index: int = 0
    current_bid_timer: Optional[int] = 15  # seconds
    bid_increment: int = 1000
    
    def add_player(self, player: AuctionPlayer):
        """Add player to auction"""
        self.players.append(player)
    
    def get_current_player(self) -> Optional[AuctionPlayer]:
        """Get current player up for auction"""
        if self.current_player_index < len(self.players):
            return self.players[self.current_player_index]
        return None
    
    def move_to_next_player(self) -> bool:
        """Move to next player"""
        current = self.get_current_player()
        if current and current.status == "available":
            current.unsold()
            self.unsold_players.append(current)
        
        self.current_player_index += 1
        return self.current_player_index < len(self.players)
    
    def sell_current_player(self) -> Optional[AuctionPlayer]:
        """Sell current player to highest bidder"""
        current = self.get_current_player()
        if current and current.current_bidder:
            current.sell()
            self.sold_players.append(current)
            self.move_to_next_player()
            return current
        return None
    
    def get_participant(self, user_id: int) -> Optional[Dict]:
        """Get participant by user_id"""
        for p in self.participants:
            if p.get("user_id") == user_id:
                return p
        return None
    
    def update_participant_coins(self, user_id: int, amount: int) -> bool:
        """Update participant coins after purchase"""
        participant = self.get_participant(user_id)
        if participant and participant.get("coins", 0) >= amount:
            participant["coins"] -= amount
            return True
        return False
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: dict) -> "Auction":
        """Create Auction from dictionary"""
        return cls(**data)

class AuctionSession(BaseModel):
    """Live auction session for fast access"""
    auction_id: str
    status: AuctionStatus = "waiting"
    current_player: Optional[AuctionPlayer] = None
    current_bid: int = 0
    current_bidder: Optional[int] = None
    timer_remaining: int = 15
    bid_history: List[Dict] = Field(default_factory=list)
    last_update: datetime = Field(default_factory=datetime.now)
    
    def start_bidding(self, player: AuctionPlayer):
        """Start bidding for a player"""
        self.current_player = player
        self.current_bid = player.base_price
        self.current_bidder = None
        self.timer_remaining = 15
        self.last_update = datetime.now()
    
    def place_bid(self, user_id: int, amount: int) -> bool:
        """Place a bid"""
        if amount > self.current_bid:
            self.current_bid = amount
            self.current_bidder = user_id
            self.timer_remaining = 15
            self.last_update = datetime.now()
            self.bid_history.append({
                "user_id": user_id,
                "amount": amount,
                "timestamp": datetime.now()
            })
            return True
        return False
    
    def decrement_timer(self) -> int:
        """Decrement timer by 1 second"""
        if self.timer_remaining > 0:
            self.timer_remaining -= 1
        return self.timer_remaining
    
    def is_time_up(self) -> bool:
        """Check if bidding time is up"""
        return self.timer_remaining <= 0
    
    def reset_for_next_player(self):
        """Reset session for next player"""
        self.current_player = None
        self.current_bid = 0
        self.current_bidder = None
        self.timer_remaining = 15
        self.bid_history.clear()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return self.model_dump()
