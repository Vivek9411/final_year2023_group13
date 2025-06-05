from app import app, db
from models import User
from sqlalchemy import text

def update_database():
    """
    Update database schema to add missing columns to the user table
    """
    print("Starting database update...")
    
    # Check if columns exist and add them if they don't
    with app.app_context():
        print("Checking for missing columns...")
        
        # Get current columns from the user table
        result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user'"))
        existing_columns = [row[0] for row in result.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Add missing columns
        if 'weight' not in existing_columns:
            print("Adding weight column...")
            db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN weight FLOAT"))
        
        if 'height' not in existing_columns:
            print("Adding height column...")
            db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN height FLOAT"))
        
        if 'age' not in existing_columns:
            print("Adding age column...")
            db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN age INTEGER"))
        
        if 'gender' not in existing_columns:
            print("Adding gender column...")
            db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN gender VARCHAR(10)"))
        
        if 'activity_level' not in existing_columns:
            print("Adding activity_level column...")
            db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN activity_level VARCHAR(20)"))
        
        if 'motive' not in existing_columns:
            print("Adding motive column...")
            db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN motive VARCHAR(20)"))
        
        # Commit the changes
        db.session.commit()
        print("Database update completed successfully")

if __name__ == '__main__':
    update_database()