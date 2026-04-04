from datetime import datetime
from typing import Optional, List, Dict, Literal
from pydantic import BaseModel, Field

MatchType = Literal["solo", "team", "tournament"]
MatchStatus = Literal["waiting", "ready", "live", "completed", "cancelled"]
TossResult = Literal["bat", "bowl"]

class BallEvent(BaseModel):
    """Single ball event"""
    ball_number: int
    over_number: int
    ball_in_over: int
    runs: int
    is_wicket: bool
    wicket_type: Optional[str] = None
    batsman: Optional[str] = None
    bowler: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class Innings(BaseModel):
    """Single innings data"""
    team_name: str
    runs: int = 0
    wickets: int = 0
    overs: float = 0.0
    balls: int = 0
    ball_events: List[BallEvent] = Field(default_factory=list)
    batsmen: List[Dict] = Field(default_factory=list)
    bowlers: List[Dict] = Field(default_factory=list)
    
    def add_ball(self, ball_event: BallEvent):
        """Add ball event to innings"""
        self.ball_events.append(ball_event)
        if not ball_event.is_wicket:
            self.runs += ball_event.runs
        else:
            self.wickets += 1
        
        self.balls += 1
        self.overs = self.balls / 6
    
    def get_current_score(self) -> str:
        """Get current score string"""
        return f"{self.runs}/{self.wickets} ({self.overs:.1f})"
    
    def is_innings_over(self) -> bool:
        """Check if innings is over"""
        return self.wickets >= 10 or (self.overs >= self.max_overs if hasattr(self, 'max_overs') else False)

class Match(BaseModel):
    """Complete match model"""
    match_id: str
    match_type: MatchType = "team"
    status: MatchStatus = "waiting"
    
    # Teams
    team_a_name: str = "Team A"
    team_b_name: str = "Team B"
    team_a_players: List[Dict] = Field(default_factory=list)
    team_b_players: List[Dict] = Field(default_factory=list)
    
    # Match settings
    total_overs: int = 2
    host_id: int
    created_by: int
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Toss
    toss_winner: Optional[int] = None
    toss_decision: Optional[TossResult] = None
    batting_first: Optional[str] = None
    bowling_first: Optional[str] = None
    
    # Innings
    innings_1: Optional[Innings] = None
    innings_2: Optional[Innings] = None
    current_innings: int = 1
    
    # Result
    winner: Optional[str] = None
    win_margin: Optional[str] = None
    man_of_match: Optional[str] = None
    
    def start_match(self):
        """Start the match"""
        self.status = "live"
        self.started_at = datetime.now()
        self.innings_1 = Innings(team_name=self.batting_first or self.team_a_name)
    
    def end_innings(self) -> bool:
        """End current innings, move to next if needed"""
        if self.current_innings == 1:
            self.current_innings = 2
            self.innings_2 = Innings(team_name=self.bowling_first or self.team_b_name)
            return True
        else:
            self.status = "completed"
            self.completed_at = datetime.now()
            self._calculate_result()
            return False
    
    def _calculate_result(self):
        """Calculate match result"""
        if not self.innings_1 or not self.innings_2:
            return
        
        team_a_score = self.innings_1.runs if self.batting_first == self.team_a_name else self.innings_2.runs
        team_b_score = self.innings_2.runs if self.batting_first == self.team_a_name else self.innings_1.runs
        
        if team_a_score > team_b_score:
            self.winner = self.team_a_name
            margin = team_a_score - team_b_score
            self.win_margin = f"{margin} runs"
        elif team_b_score > team_a_score:
            self.winner = self.team_b_name
            margin = team_b_score - team_a_score
            self.win_margin = f"{margin} runs"
        else:
            self.winner = "Tie"
            self.win_margin = "Match Tied"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = self.model_dump()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "Match":
        """Create Match from dictionary"""
        return cls(**data)

class MatchSession(BaseModel):
    """Live match session for fast access"""
    match_id: str
    current_over: int = 0
    current_ball: int = 0
    current_runs: int = 0
    current_wickets: int = 0
    target_runs: Optional[int] = None
    striker: Optional[Dict] = None
    non_striker: Optional[Dict] = None
    current_bowler: Optional[Dict] = None
    last_ball: Optional[BallEvent] = None
    waiting_for: Literal["bowling", "batting", None] = None
    last_update: datetime = Field(default_factory=datetime.now)
    
    def update_after_ball(self, ball_event: BallEvent):
        """Update session after ball"""
        self.last_ball = ball_event
        self.last_update = datetime.now()
        
        if not ball_event.is_wicket:
            self.current_runs += ball_event.runs
        else:
            self.current_wickets += 1
        
        self.current_ball += 1
        if self.current_ball == 6:
            self.current_over += 1
            self.current_ball = 0
    
    def is_match_over(self, max_overs: int) -> bool:
        """Check if match is over"""
        return self.current_over >= max_overs or self.current_wickets >= 10
    
    def get_required_runs(self) -> str:
        """Get required runs if chasing"""
        if self.target_runs and self.current_runs < self.target_runs:
            required = self.target_runs - self.current_runs
            return f"Need {required} runs"
        return "Target achieved!"
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return self.model_dump()
