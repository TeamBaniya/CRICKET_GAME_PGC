# TODO: Add your code here
import random
from typing import Dict, Tuple, List

class CricketEngine:
    """Main cricket game logic"""
    
    # Possible runs on each ball (with probabilities)
    RUNS_POSSIBLE = [0, 1, 2, 3, 4, 6]
    # Wicket probability (1 in 12 balls approx)
    WICKET_PROBABILITY = 0.08
    
    def __init__(self, overs: int):
        self.total_overs = overs
        self.max_balls = overs * 6
        self.current_ball = 0
        self.runs = 0
        self.wickets = 0
        self.balls_in_over = 0
        self.current_over = 0
        self.ball_by_ball = []
        
    def play_ball(self) -> Dict:
        """Play a single ball, return result"""
        self.current_ball += 1
        self.balls_in_over += 1
        
        # Update over count
        if self.balls_in_over == 6:
            self.current_over += 1
            self.balls_in_over = 0
        
        # Check wicket
        is_wicket = random.random() < self.WICKET_PROBABILITY
        
        if is_wicket:
            self.wickets += 1
            result = {
                "ball": self.current_ball,
                "over": self.current_over,
                "ball_in_over": self.balls_in_over or 6,
                "runs": 0,
                "is_wicket": True,
                "wicket_type": self._get_wicket_type(),
                "total_runs": self.runs,
                "total_wickets": self.wickets
            }
        else:
            runs = random.choice(self.RUNS_POSSIBLE)
            self.runs += runs
            result = {
                "ball": self.current_ball,
                "over": self.current_over,
                "ball_in_over": self.balls_in_over or 6,
                "runs": runs,
                "is_wicket": False,
                "wicket_type": None,
                "total_runs": self.runs,
                "total_wickets": self.wickets
            }
        
        self.ball_by_ball.append(result)
        return result
    
    def is_match_over(self) -> bool:
        """Check if match is over"""
        return self.current_ball >= self.max_balls or self.wickets >= 10
    
    def get_current_score(self) -> str:
        """Get current score string"""
        return f"{self.runs}/{self.wickets} ({self.current_over}.{self.balls_in_over})"
    
    def get_required_runs(self, target: int) -> str:
        """Get required runs if chasing"""
        if self.runs >= target:
            return "Target achieved!"
        required = target - self.runs
        balls_left = self.max_balls - self.current_ball
        return f"Need {required} runs in {balls_left} balls"
    
    def _get_wicket_type(self) -> str:
        """Random wicket type"""
        wicket_types = ["Bowled 🎯", "Caught 🧤", "LBW 📏", "Run Out 🏃", "Stumped 🪤"]
        return random.choice(wicket_types)
    
    def get_match_summary(self) -> str:
        """Get full match summary"""
        summary = f"🏏 **Match Summary**\n\n"
        summary += f"📊 Score: {self.runs}/{self.wickets}\n"
        summary += f"📈 Overs: {self.current_over}.{self.balls_in_over}/{self.total_overs}\n"
        summary += f"⚡ Balls: {self.current_ball}/{self.max_balls}\n"
        
        # Strike rate
        if self.current_ball > 0:
            strike_rate = (self.runs / self.current_ball) * 100
            summary += f"🎯 Strike Rate: {strike_rate:.2f}\n"
        
        return summary

def calculate_runs(hitter_rating: int, bowler_rating: int) -> int:
    """Calculate runs based on player ratings"""
    base_runs = random.choice([0, 1, 2, 3, 4, 6])
    # Higher rating gives more chances of boundaries
    if hitter_rating > bowler_rating and random.random() > 0.5:
        if base_runs == 4:
            base_runs = 6
        elif base_runs == 1:
            base_runs = 4
    return base_runs

def calculate_wicket(bowler_rating: int, hitter_rating: int) -> bool:
    """Calculate if wicket occurs"""
    chance = 0.05 + (bowler_rating - hitter_rating) * 0.02
    chance = max(0.02, min(0.15, chance))  # Between 2% and 15%
    return random.random() < chance

def toss_winner(team_a_captain: str, team_b_captain: str) -> Tuple[str, str]:
    """Toss winner and decision"""
    winner = random.choice([team_a_captain, team_b_captain])
    decision = random.choice(["bat", "bowl"])
    
    toss_result = {
        "winner": winner,
        "decision": decision,
        "batting_first": winner if decision == "bat" else (team_b_captain if winner == team_a_captain else team_a_captain),
        "bowling_first": winner if decision == "bowl" else (team_b_captain if winner == team_a_captain else team_a_captain)
    }
    return toss_result

def update_score(current_score: Dict, runs: int, is_wicket: bool) -> Dict:
    """Update score after each ball"""
    new_score = current_score.copy()
    if is_wicket:
        new_score["wickets"] += 1
    else:
        new_score["runs"] += runs
    new_score["balls"] += 1
    new_score["overs"] = new_score["balls"] // 6
    new_score["balls_in_over"] = new_score["balls"] % 6
    return new_score

class TeamStats:
    """Team statistics tracking"""
    def __init__(self, team_name: str, players: List[Dict]):
        self.team_name = team_name
        self.players = players
        self.score = 0
        self.wickets = 0
        self.overs = 0
        self.balls = 0
        self.current_batsman = players[0] if players else None
        self.current_non_striker = players[1] if len(players) > 1 else None
        self.current_bowler = None
        
    def add_runs(self, runs: int):
        self.score += runs
        # Swap strike on odd runs
        if runs % 2 == 1 and self.current_batsman and self.current_non_striker:
            self.current_batsman, self.current_non_striker = self.current_non_striker, self.current_batsman
    
    def wicket_fall(self):
        self.wickets += 1
        # Next batsman comes in
        if self.wickets + 1 < len(self.players):
            self.current_batsman = self.players[self.wickets + 1]
