"""
Start the FastAPI development server.

This script starts uvicorn with the correct parameters for development.
"""
import subprocess
import sys

print("=" * 70)
print("Starting LeadFlow API Server")
print("=" * 70)
print()
print("Server will start on: http://localhost:8000")
print("API Documentation: http://localhost:8000/docs")
print("Health Check: http://localhost:8000/health")
print()
print("Press Ctrl+C to stop the server")
print("=" * 70)
print()

try:
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--reload",
        "--port", "8000",
        "--host", "0.0.0.0"
    ])
except KeyboardInterrupt:
    print("\nServer stopped")
