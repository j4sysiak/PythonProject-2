"""
Script to reset the database SQLite schema for tests or development.
Usage (from project root):
    python -m MiniBank.scripts.reset_db

It drops all tables and recreates them using SQLAlchemy metadata.
Be careful: this will destroy all data in the configured DATABASE_URL.
"""
import argparse
import asyncio
import os


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Reset DB schema (drop+create) for MiniBank")
    p.add_argument("--url", help="Database URL to use (overrides DATABASE_URL env)", required=False)
    p.add_argument("--yes", help="Don't ask for confirmation", action="store_true")
    return p.parse_args()


async def _do_reset():
    # Import AFTER environment is set so MiniBank.database reads the correct URL
    from MiniBank.database import DATABASE_URL, engine
    from MiniBank.models import Base

    print(f"Resetting database at {DATABASE_URL}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Done.")


def main():
    args = parse_args()
    # Resolve which URL we will use (priority: --url, env DATABASE_URL, fallback to local sqlite)
    default_sqlite = "sqlite+aiosqlite:///./test_minibank.db"
    resolved_url = args.url or os.environ.get("DATABASE_URL") or default_sqlite

    # Safety: if using a postgres-like URL but user didn't explicitly pass --url, warn prominently
    if resolved_url.startswith("postgres") and not args.url:
        print("WARNING: resolved DATABASE_URL looks like a Postgres URL and --url was not provided.")
        print("This script will try to connect to the URL from environment or defaults. To be safe, pass --url explicitly.")

    # Export the resolved value so MiniBank.database will pick it up when imported later
    os.environ["DATABASE_URL"] = resolved_url

    if not args.yes:
        confirm = input(f"This will DROP and CREATE ALL TABLES in {resolved_url}. Continue? [y/N]: ")
        if confirm.lower() != 'y':
            print("Aborting.")
            return

    asyncio.run(_do_reset())


if __name__ == '__main__':
    main()
