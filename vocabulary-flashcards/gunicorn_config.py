import os

# Railway sets the PORT environment variable
port = os.environ.get("PORT", "8080") # Default to 8080 if not set, but Railway ALWAYS sets PORT
bind = f"0.0.0.0:{port}"

# Worker configuration
workers = 4
threads = 2
timeout = 120
