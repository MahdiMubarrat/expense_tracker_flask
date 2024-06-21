from app import app, db
from sqlalchemy import inspect

def create_tables():
    with app.app_context():
        try:
            print("Creating database tables...")
            db.create_all()
            print("Database tables created.")
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Tables in the database: {tables}")
        except Exception as e:
            print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()