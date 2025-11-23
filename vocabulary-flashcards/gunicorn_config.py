import os

# Railway sets the PORT environment variable
port = os.environ.get("PORT", "8000")
bind = f"0.0.0.0:{port}"

# Worker configuration
workers = 4
threads = 2
timeout = 120
