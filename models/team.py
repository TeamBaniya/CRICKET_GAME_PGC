from datetime import datetime
from typing import Optional, List, Dict, Literal
from pydantic import BaseModel, Field

PlayerRole = Literal["batsman", "bowler", "all_rounder", "wicket_keeper"]
BattingHand = Literal["right", "left"]
BowlingType = Literal["fast", "medium", "spin", "leg_spin", "off_spin"]

class TeamPlayer(BaseModel):
    """Team player model"""
    user_id: int
    username: Optional[str] = None
    first_name: str
    player_number: int
    role: PlayerRole = "batsman"
    batting_hand: BattingHand = "right"
    bowling_type: Optional[BowlingType] = None
    rating: int = 50
    
    # Match stats for current match
    runs_scored: int = 0
    balls_faced: int = 0
    wickets_taken: int = 0
    runs_conceded: int = 0
    overs_bowled: float = 0.0
    catches: int = 0
    
    @property
    def strike_rate(self) -> float:
        if self.balls_faced == 0:
            return 0.0
        return (self.runs_scored / self.balls_faced) * 100
    
    @property
    def economy(self) -> float:
        if self.overs_bowled == 0:
            return 0.0
        return self.runs_conceded / self.overs_bowled
    
    def add_runs(self, runs: int, balls: int = 1):
        """Add runs to player"""
        self.runs_scored += runs
        self.balls_faced += balls
    
    def add_wicket(self, runs_conceded: int, overs: float):
        """Add wicket to player"""
        self.wickets_taken += 1
        self.runs_conceded += runs_conceded
        self.overs_bowled += overs
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return self.model_dump()

class Team(BaseModel):
    """Team model"""
    team_id: str
    team_name: str
    team_color: Literal["blue", "red", "green", "yellow", "black"] = "blue"
    captain_id: Optional[int] = None
    vice_captain_id: Optional[int] = None
    players: List[TeamPlayer] = Field(default_factory=list)
    created_by: int
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Team stats
    total_matches: int = 0
    total_wins: int = 0
    total_losses: int = 0
    
    @property
    def win_rate(self) -> float:
        if self.total_matches == 0:
            return 0.0
        return (self.total_wins / self.total_matches) * 100
    
    def add_player(self, player: TeamPlayer):
        """Add player to team"""
        self.players.append(player)
    
    def remove_player(self, player_number: int) -> bool:
        """Remove player by number"""
        for i, p in enumerate(self.players):
            if p.player_number == player_number:
                self.players.pop(i)
                return True
        return False
    
    def get_player_by_number(self, player_number: int) -> Optional[TeamPlayer]:
        """Get player by number"""
        for p in self.players:
            if p.player_number == player_number:
                return p
        return None
    
    def get_player_by_user_id(self, user_id: int) -> Optional[TeamPlayer]:
        """Get player by user_id"""
        for p in self.players:
            if p.user_id == user_id:
                return p
        return None
    
    def set_captain(self, player_number: int) -> bool:
        """Set team captain"""
        player = self.get_player_by_number(player_number)
        if player:
            self.captain_id = player.user_id
            return True
        return False
    
    def get_players_list(self) -> List[str]:
        """Get formatted players list"""
        return [f"{p.player_number}. {p.first_name} ({p.role})" for p in self.players]
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: dict) -> "Team":
        """Create Team from dictionary"""
        return cls(**data)

class TeamMatchStats(BaseModel):
    """Team match statistics"""
    match_id: str
    team_id: str
    team_name: str
    runs: int = 0
    wickets: int = 0
    overs: float = 0.0
    extras: int = 0
    player_stats: Dict[int, Dict] = Field(default_factory=dict)  # user_id -> stats
    
    def add_player_stats(self, user_id: int, runs: int = 0, wickets: int = 0, catches: int = 0):
        """Add player statistics"""
        if user_id not in self.player_stats:
            self.player_stats[user_id] = {"runs": 0, "wickets": 0, "catches": 0}
        
        self.player_stats[user_id]["runs"] += runs
        self.player_stats[user_id]["wickets"] += wickets
        self.player_stats[user_id]["catches"] += catches
        self.runs += runs
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return self.model_dump()
