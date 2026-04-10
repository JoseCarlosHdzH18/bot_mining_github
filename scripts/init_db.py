#!/usr/bin/env python3
"""Initialize database tables."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import init_db, engine
from app.db.models import Job, Repository, User, Technology, JobExecutionLog


def main():
    print("🗄️ Creating database tables...")
    
    init_db()
    
    print("✅ Database initialized successfully!")
    
    with engine.connect() as conn:
        result = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [row[0] for row in result]
        print(f"📋 Tables created: {', '.join(tables)}")


if __name__ == "__main__":
    main()
