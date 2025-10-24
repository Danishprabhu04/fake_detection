import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.scripts.data_ingestion import main as data_ingestion_main
from app.scripts.setup_models import main as setup_models_main
from app.scripts.mongodb_setup import main as mongodb_setup_main

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please specify which script to run:")
        print("  python tester.py mongodb_setup")
        print("  python tester.py data_ingestion")
        print("  python tester.py setup_models")
        sys.exit(1)

    script = sys.argv[1]
    if script == "mongodb_setup":
        mongodb_setup_main()
    elif script == "data_ingestion":
        data_ingestion_main()
    elif script == "setup_models":
        setup_models_main()
    else:
        print(f"Unknown script: {script}")