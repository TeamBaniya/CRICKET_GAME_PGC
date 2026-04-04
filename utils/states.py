# TODO: Add your code here
from typing import Dict, Optional
from datetime import datetime

# User states
class STATES:
    MAIN_MENU = "main_menu"
    HOST_SELECT = "host_select"
    TEAM_CREATION = "team_creation"
    WAITING_PLAYERS = "waiting_players"
    OVERS_SELECT = "overs_select"
    MATCH_READY = "match_ready"
    MATCH_LIVE = "match_live"
    WAITING_BOWLING = "waiting_bowling"
    WAITING_BATTING = "waiting_batting"
    AUCTION_MODE = "auction_mode"
    AUCTION_LIVE = "auction_live"
    HELP_MENU = "help_menu"
    GAME_INSTRUCTIONS = "game_instructions"
    SOLO_MODE = "solo_mode"
    TEAM_MODE = "team_mode"

class UserState:
    """Individual user state management"""
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.state = STATES.MAIN_MENU
        self.last_activity = datetime.now()
        self.temp_data = {}
        
        # Match related
        self.current_match_id = None
        self.current_team = None  # "A" or "B"
        self.is_host = False
        
        # Auction related
        self.auction_id = None
        self.current_bid = 0
        
    def update_state(self, new_state: str, data: Dict = None):
        """Update user state"""
        self.state = new_state
        self.last_activity = datetime.now()
        if data:
            self.temp_data.update(data)
    
    def get_temp(self, key: str, default=None):
        """Get temporary data"""
        return self.temp_data.get(key, default)
    
    def clear_temp(self):
        """Clear temporary data"""
        self.temp_data.clear()
    
    def is_active(self, timeout_minutes: int = 30) -> bool:
        """Check if user is still active"""
        delta = datetime.now() - self.last_activity
        return delta.total_seconds() < (timeout_minutes * 60)

class StateManager:
    """Global state manager for all users"""
    def __init__(self):
        self._states: Dict[int, UserState] = {}
        self._match_states: Dict[str, Dict] = {}  # match_id -> match state
    
    def get_user_state(self, user_id: int) -> UserState:
        """Get or create user state"""
        if user_id not in self._states:
            self._states[user_id] = UserState(user_id)
        return self._states[user_id]
    
    def update_user_state(self, user_id: int, new_state: str, data: Dict = None):
        """Update user state"""
        state = self.get_user_state(user_id)
        state.update_state(new_state, data)
    
    def get_match_state(self, match_id: str) -> Optional[Dict]:
        """Get match state"""
        return self._match_states.get(match_id)
    
    def update_match_state(self, match_id: str, data: Dict):
        """Update match state"""
        if match_id not in self._match_states:
            self._match_states[match_id] = {}
        self._match_states[match_id].update(data)
    
    def delete_match_state(self, match_id: str):
        """Delete match state"""
        if match_id in self._match_states:
            del self._match_states[match_id]
    
    def clear_inactive_states(self, timeout_minutes: int = 30):
        """Clear inactive user states"""
        to_delete = []
        for user_id, state in self._states.items():
            if not state.is_active(timeout_minutes):
                to_delete.append(user_id)
        for user_id in to_delete:
            del self._states[user_id]
    
    def get_active_users_count(self) -> int:
        """Get count of active users"""
        return len(self._states)

# Global state manager instance
state_manager = StateManager()
