"""
Launcher script for Streamlit app
"""
import subprocess
import sys

def main():
    print("="*80)
    print("Dubai Real Estate Price Predictor - Streamlit App")
    print("="*80)
    print()
    print("Starting Streamlit app...")
    print("App will open in your browser at http://localhost:8501")
    print("Press Ctrl+C to stop the server")
    print()
    print("="*80)
    print()

    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n\nShutting down Streamlit app...")
        print("Goodbye!")
    except Exception as e:
        print(f"\nError starting Streamlit: {e}")
        print("\nMake sure streamlit is installed:")
        print("  pip install streamlit")

if __name__ == "__main__":
    main()
