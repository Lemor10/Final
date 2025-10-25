import os

class Config:
    # PostgreSQL database connection
    # This will first try to load the DATABASE_URL from environment variables (Render)
    # If not found, it falls back to a local connection
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://final_krsw_user:lzWJqegt9I3nGdqw9DohfXHRnOYpFQFj@dpg-d3ucdj8dl3ps73f1m7tg-a/final_krsw"
    )

    # Disable modification tracking (to save memory)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key for session management and CSRF protection
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

    # Optional: Uploads or file storage configuration
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Optional: Debug mode (set False in production)
    DEBUG = True
