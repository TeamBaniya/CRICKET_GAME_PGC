// Create database
db = db.getSiblingDB('cricket_bot');

// Create collections
db.createCollection('users');
db.createCollection('matches');
db.createCollection('sessions');
db.createCollection('auctions');
db.createCollection('teams');

// Create indexes for better performance
db.users.createIndex({ "user_id": 1 }, { unique: true });
db.users.createIndex({ "last_active": -1 });
db.users.createIndex({ "is_active": 1 });

db.matches.createIndex({ "match_id": 1 }, { unique: true });
db.matches.createIndex({ "status": 1 });
db.matches.createIndex({ "created_at": -1 });

db.sessions.createIndex({ "match_id": 1 }, { unique: true });
db.sessions.createIndex({ "last_update": -1 });

db.auctions.createIndex({ "auction_id": 1 }, { unique: true });
db.auctions.createIndex({ "status": 1 });
db.auctions.createIndex({ "host_id": 1 });

db.teams.createIndex({ "team_id": 1 }, { unique: true });
db.teams.createIndex({ "created_by": 1 });

// Create TTL index for sessions (auto-delete after 1 hour)
db.sessions.createIndex({ "last_update": 1 }, { expireAfterSeconds: 3600 });

print('MongoDB initialization completed!');
