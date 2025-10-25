import sys

from app.scripts.train_models import main as train_models_main

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please specify which script to run:")
        print("  python tester.py mongodb_setup")
        print("  python tester.py data_ingestion")
        print("  python tester.py train_models")  # Add this line
        sys.exit(1)

    script = sys.argv[1]
    if script == "train_models":
        train_models_main()
    else:
        print(f"Unknown script: {script}")