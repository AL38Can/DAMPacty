from database import Database

def migrate():
    """Run the database migration."""
    try:
        db = Database()
        db.migrate_from_json()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate() 