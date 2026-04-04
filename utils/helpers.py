import re
from datetime import datetime
from typing import Optional

def format_score(runs: int, wickets: int, overs: float) -> str:
    """Format score as 'runs/wickets (overs)'"""
    return f"{runs}/{wickets} ({overs})"

def format_overs(balls: int) -> str:
    """Convert balls to overs format (e.g., 25 balls -> 4.1 overs)"""
    overs = balls // 6
    remaining_balls = balls % 6
    return f"{overs}.{remaining_balls}"

def validate_player_number(player_input: str, max_players: int = 11) -> Optional[int]:
    """Validate player number input"""
    try:
        num = int(player_input)
        if 1 <= num <= max_players:
            return num
    except ValueError:
        pass
    return None

def get_player_name(username: str, first_name: str = None) -> str:
    """Get formatted player name"""
    if username:
        return f"@{username}"
    return first_name or "Unknown Player"

def parse_command_args(text: str) -> tuple:
    """Parse command and arguments"""
    parts = text.split()
    if len(parts) < 2:
        return None, []
    return parts[0], parts[1:]

def extract_username(text: str) -> Optional[str]:
    """Extract username from text"""
    match = re.search(r'@(\w+)', text)
    if match:
        return match.group(1)
    return None

def is_valid_overs(overs: int) -> bool:
    """Check if overs is valid (1-7)"""
    return 1 <= overs <= 7

def calculate_strike_rate(runs: int, balls: int) -> float:
    """Calculate strike rate"""
    if balls == 0:
        return 0.0
    return (runs / balls) * 100

def calculate_economy(runs: int, overs: float) -> float:
    """Calculate economy rate"""
    if overs == 0:
        return 0.0
    return runs / overs

async def send_feedback(client, user_id: int, feedback: str):
    """Send feedback to admin"""
    admin_id = 123456789  # Your admin ID
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"📝 **New Feedback**\n\n"
    message += f"👤 User: `{user_id}`\n"
    message += f"⏰ Time: {timestamp}\n\n"
    message += f"💬 {feedback}"
    
    await client.send_message(admin_id, message)

def get_emoji_for_runs(runs: int) -> str:
    """Get emoji for runs"""
    if runs == 0:
        return "⚪"
    elif runs == 4:
        return "🟢 4️⃣"
    elif runs == 6:
        return "🔴 6️⃣"
    elif runs == 1:
        return "1️⃣"
    elif runs == 2:
        return "2️⃣"
    elif runs == 3:
        return "3️⃣"
    return "⚫"

def get_wicket_emoji(wicket_type: str) -> str:
    """Get emoji for wicket type"""
    emojis = {
        "Bowled": "🎯",
        "Caught": "🧤",
        "LBW": "📏",
        "Run Out": "🏃",
        "Stumped": "🪤"
    }
    for key, emoji in emojis.items():
        if key in wicket_type:
            return emoji
    return "❌"

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Create a progress bar"""
    filled = int((current / total) * length)
    empty = length - filled
    return "█" * filled + "░" * empty
