import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'lux-salon-finder-super-secret-key-2026'
    # Parse Supabase connection URI to postgresql+pg8000:// to use the pg8000 driver
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Strip query parameters (like sslmode) because pg8000 does not accept them directly
        if '?' in database_url:
            database_url = database_url.split('?')[0]
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+pg8000://", 1)
        elif database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+pg8000://", 1)

    SQLALCHEMY_DATABASE_URI = database_url or 'postgresql+pg8000://postgres.ryewzzdytcehcizcqshc:aadhihdya2905@aws-0-ap-south-1.pooler.supabase.com:6543/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
