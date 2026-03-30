import os
import asyncio
from datetime import datetime, timezone
from decimal import Decimal

os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:///C:/dev/python-projects/PycharmProjects/PythonProject-2/test_minibank.db')

from MiniBank.database import AsyncSessionLocal, engine, Base
from MiniBank.models import TransactionHistory

async def main():
    async with AsyncSessionLocal() as session:
        tx = TransactionHistory(from_account_id=1, to_account_id=2, amount=Decimal('10'), note='tmp test', timestamp=datetime.now(timezone.utc))
        session.add(tx)
        await session.commit()
        print('Inserted tx id', tx.id)

if __name__ == '__main__':
    asyncio.run(main())

