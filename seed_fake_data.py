"""
Reset the Gym Platform database and refill it with demo data.

This WIPES every table, then regenerates the full demo dataset (members,
employees, products, payments, expenses, purchases, today's check-ins and
activity/audit logs) so every tab in the app has something to show.

Usage:
    python seed_fake_data.py            # asks for confirmation first
    python seed_fake_data.py --yes      # skip the confirmation prompt

Targets whatever database the app uses (PostgreSQL if available, else the
local SQLite file). Login afterwards with:  admin / admin123
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.database import engine, Base
from backend.seed import seed_data


def main():
    target = engine.url.render_as_string(hide_password=True)
    print("=" * 60)
    print("  Gym Platform — reset & demo-data seeder")
    print("=" * 60)
    print(f"  Target database: {target}")
    print("  This DELETES all existing data and replaces it with demo data.")

    if "--yes" not in sys.argv:
        try:
            ans = input("  Type 'yes' to continue: ").strip().lower()
        except EOFError:
            ans = ""
        if ans not in ("yes", "y"):
            print("  Aborted. (run with --yes to skip this prompt)")
            return

    print("[seed] Dropping and recreating all tables…")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_data()
    print("[seed] Done.")


if __name__ == "__main__":
    main()
