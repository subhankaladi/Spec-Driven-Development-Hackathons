"""
Test database connection script
Run this to verify your Neon PostgreSQL connection
"""
from sqlmodel import Session, select
from sqlalchemy import text
from src.database.session import engine
from src.config.settings import settings


def test_connection():
    """Test database connection"""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)

    print(f"\n[INFO] Database Type: {'PostgreSQL (Neon)' if settings.is_postgresql else 'SQLite'}")
    print(f"[INFO] Connection URL: {settings.database_url[:50]}...")
    print(f"[INFO] Environment: {settings.environment}")

    try:
        # Test connection
        with Session(engine) as session:
            result = session.exec(select(1)).one()
            print(f"\n[SUCCESS] Connection successful!")
            print(f"   Test query result: {result}")

            # Get database version
            if settings.is_postgresql:
                version_result = session.exec(text("SELECT version()")).one()
                print(f"   PostgreSQL version: {version_result[:60]}...")
            else:
                print(f"   Using SQLite (local file)")

            print("\n[SUCCESS] Database is ready to use!")
            return True

    except Exception as e:
        print(f"\n[ERROR] Connection failed!")
        print(f"   Error: {str(e)}")
        print("\n[TIPS] Troubleshooting:")
        print("   1. Check your .env file has the correct DATABASE_URL")
        print("   2. Verify the Neon connection string is correct")
        print("   3. Ensure psycopg2-binary is installed: pip install psycopg2-binary")
        print("   4. Check if your Neon project is active at https://console.neon.tech")
        return False


if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)
