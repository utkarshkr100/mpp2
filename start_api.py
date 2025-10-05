"""
Launcher script for FastAPI server
"""
import subprocess
import sys

def main():
    print("="*80)
    print("Dubai Real Estate Price Predictor - FastAPI Server")
    print("="*80)
    print()
    print("Starting FastAPI server...")
    print("API will be available at http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print()
    print("="*80)
    print()

    try:
        subprocess.run([sys.executable, "api.py"])
    except KeyboardInterrupt:
        print("\n\nShutting down API server...")
        print("Goodbye!")
    except Exception as e:
        print(f"\nError starting API: {e}")
        print("\nMake sure FastAPI and uvicorn are installed:")
        print("  pip install fastapi uvicorn")

if __name__ == "__main__":
    main()
