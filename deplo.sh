#!/bin/bash

# Cricket Bot Deployment Script
# Author: Cricket Bot Developer
# Usage: ./deploy.sh [option]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    echo -e "${2}${1}${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_message "⚠️  Running as root is not recommended!" "$YELLOW"
    fi
}

# Check required commands
check_requirements() {
    print_message "🔍 Checking requirements..." "$BLUE"
    
    commands=("python3" "pip3" "docker" "docker-compose" "git")
    for cmd in "${commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            print_message "❌ $cmd is not installed!" "$RED"
            exit 1
        fi
    done
    
    print_message "✅ All requirements satisfied!" "$GREEN"
}

# Setup environment
setup_env() {
    print_message "🔧 Setting up environment..." "$BLUE"
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_message "📝 Created .env file. Please edit it with your credentials!" "$YELLOW"
        print_message "   Run: nano .env" "$YELLOW"
        
        # Ask if user wants to edit now
        read -p "Do you want to edit .env now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        print_message "✅ .env file already exists" "$GREEN"
    fi
}

# Install Python dependencies
install_dependencies() {
    print_message "📦 Installing Python dependencies..." "$BLUE"
    pip3 install -r requirements.txt
    print_message "✅ Dependencies installed!" "$GREEN"
}

# Setup MongoDB
setup_mongodb() {
    print_message "🗄️  Setting up MongoDB..." "$BLUE"
    
    if ! systemctl is-active --quiet mongod; then
        print_message "⚠️  MongoDB is not running. Starting via Docker..." "$YELLOW"
        docker-compose up -d mongodb redis
        sleep 5
    fi
    
    print_message "✅ MongoDB setup complete!" "$GREEN"
}

# Run database migrations
run_migrations() {
    print_message "🔄 Running database migrations..." "$BLUE"
    
    # Initialize MongoDB indexes
    python3 -c "
from database import db
import asyncio

async def init():
    await db.users.create_index('user_id', unique=True)
    await db.matches.create_index('match_id', unique=True)
    await db.sessions.create_index('match_id', unique=True)
    print('✅ Database indexes created!')

asyncio.run(init())
"
    print_message "✅ Migrations complete!" "$GREEN"
}

# Start the bot
start_bot() {
    print_message "🚀 Starting Cricket Bot..." "$BLUE"
    
    # Check if bot is already running
    if pgrep -f "python3 main.py" > /dev/null; then
        print_message "⚠️  Bot is already running!" "$YELLOW"
        read -p "Do you want to restart? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            stop_bot
        else
            return
        fi
    fi
    
    # Start bot with nohup
    nohup python3 main.py > logs/bot.log 2>&1 &
    echo $! > bot.pid
    
    print_message "✅ Bot started! PID: $(cat bot.pid)" "$GREEN"
    print_message "📋 View logs: tail -f logs/bot.log" "$YELLOW"
}

# Stop the bot
stop_bot() {
    print_message "🛑 Stopping Cricket Bot..." "$BLUE"
    
    if [ -f bot.pid ]; then
        kill -9 $(cat bot.pid) 2>/dev/null || true
        rm bot.pid
        print_message "✅ Bot stopped!" "$GREEN"
    else
        pkill -f "python3 main.py" || true
        print_message "✅ Bot stopped!" "$GREEN"
    fi
}

# Restart the bot
restart_bot() {
    print_message "🔄 Restarting Cricket Bot..." "$BLUE"
    stop_bot
    sleep 2
    start_bot
}

# Check bot status
status_bot() {
    print_message "📊 Bot Status:" "$BLUE"
    
    if [ -f bot.pid ] && kill -0 $(cat bot.pid) 2>/dev/null; then
        print_message "✅ Bot is running (PID: $(cat bot.pid))" "$GREEN"
    else
        print_message "❌ Bot is not running!" "$RED"
    fi
    
    # Check Docker containers
    print_message "\n🐳 Docker Containers:" "$BLUE"
    docker-compose ps
    
    # Show latest logs
    print_message "\n📋 Latest logs:" "$BLUE"
    tail -5 logs/bot.log 2>/dev/null || print_message "No logs found" "$YELLOW"
}

# Backup database
backup_db() {
    print_message "💾 Backing up database..." "$BLUE"
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $BACKUP_DIR
    
    docker-compose exec -T mongodb mongodump --out /dump
    docker cp $(docker-compose ps -q mongodb):/dump $BACKUP_DIR/
    
    print_message "✅ Backup saved to: $BACKUP_DIR" "$GREEN"
}

# Restore database
restore_db() {
    print_message "🔄 Restoring database..." "$BLUE"
    
    if [ -z "$1" ]; then
        print_message "Usage: ./deploy.sh restore <backup_path>" "$RED"
        exit 1
    fi
    
    docker cp $1/. $(docker-compose ps -q mongodb):/dump/
    docker-compose exec -T mongodb mongorestore /dump
    print_message "✅ Database restored!" "$GREEN"
}

# Update bot
update_bot() {
    print_message "🔄 Updating Cricket Bot..." "$BLUE"
    
    # Pull latest changes
    git pull origin main
    
    # Update dependencies
    pip3 install -r requirements.txt
    
    # Restart bot
    restart_bot
    
    print_message "✅ Update complete!" "$GREEN"
}

# Show logs
show_logs() {
    if [ -f logs/bot.log ]; then
        tail -f logs/bot.log
    else
        print_message "❌ No logs found!" "$RED"
    fi
}

# Docker deployment
docker_deploy() {
    print_message "🐳 Deploying with Docker..." "$BLUE"
    
    # Build and start containers
    docker-compose down
    docker-compose build
    docker-compose up -d
    
    print_message "✅ Docker deployment complete!" "$GREEN"
    print_message "📋 View logs: docker-compose logs -f" "$YELLOW"
}

# Help menu
show_help() {
    echo ""
    print_message "🏏 CRICKET BOT DEPLOYMENT SCRIPT" "$BLUE"
    echo ""
    echo "Usage: ./deploy.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  start       - Start the bot"
    echo "  stop        - Stop the bot"
    echo "  restart     - Restart the bot"
    echo "  status      - Check bot status"
    echo "  logs        - View bot logs"
    echo "  update      - Update bot to latest version"
    echo "  backup      - Backup database"
    echo "  restore     - Restore database from backup"
    echo "  docker      - Deploy using Docker"
    echo "  install     - Full installation (first time)"
    echo "  help        - Show this help menu"
    echo ""
}

# Full installation
full_install() {
    print_message "🏏 CRICKET BOT - FULL INSTALLATION" "$BLUE"
    echo ""
    
    check_root
    check_requirements
    setup_env
    install_dependencies
    setup_mongodb
    run_migrations
    
    # Create logs directory
    mkdir -p logs
    
    print_message "\n✅ Installation complete!" "$GREEN"
    print_message "\nNext steps:" "$YELLOW"
    print_message "1. Edit .env file with your bot token" "$YELLOW"
    print_message "2. Run: ./deploy.sh start" "$YELLOW"
    print_message "3. Run: ./deploy.sh status" "$YELLOW"
}

# Main script logic
case "${1:-}" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        restart_bot
        ;;
    status)
        status_bot
        ;;
    logs)
        show_logs
        ;;
    update)
        update_bot
        ;;
    backup)
        backup_db
        ;;
    restore)
        restore_db "$2"
        ;;
    docker)
        docker_deploy
        ;;
    install)
        full_install
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_message "❌ Unknown option: ${1:-none}" "$RED"
        show_help
        exit 1
        ;;
esac
