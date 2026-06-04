"""
Build the desktop application to .exe
"""
import subprocess
import sys
import os
import shutil

def build_exe():
    print("Building Gym Platform Desktop App...")
    print("=" * 50)

    # Clean old builds
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Cleaned {folder}/")

    # Build command — bundles the CustomTkinter desktop app.
    # No PostgreSQL needed at runtime: the app falls back to a local SQLite
    # database automatically (see backend/database.py).
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=Gym_Platform",
        "--windowed",
        "--noconfirm",
        "--clean",
        "--add-data=backend;backend",
        "--add-data=.env;.",
        "--collect-all=customtkinter",
        "--hidden-import=sqlite3",
        "--hidden-import=psycopg2",
        "--hidden-import=sqlalchemy",
        "--hidden-import=passlib",
        "--hidden-import=bcrypt",
        "--hidden-import=pydantic",
        "desktop_app.py"
    ]

    try:
        subprocess.check_call(cmd)
        print("\n" + "=" * 50)
        print("BUILD COMPLETE!")
        print("Executable: dist/Gym_Platform/Gym_Platform.exe")
        print("=" * 50)
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed: {e}")

if __name__ == "__main__":
    build_exe()
