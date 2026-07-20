"""
Seed script — run once after alembic upgrade head:
  python -m app.seed
"""
import asyncio
import json
import uuid
from pathlib import Path
from app.database import AsyncSessionLocal
from app.models.hs_code import HSCode
from app.models.emission_factor import EmissionFactor


async def seed() -> None:
    data_dir = Path(__file__).parent / "data"

    async with AsyncSessionLocal() as session:
        # Seed HS codes
        hs_path = data_dir / "hs_codes.json"
        hs_data = json.loads(hs_path.read_text())
        for item in hs_data:
            code = HSCode(id=str(uuid.uuid4()), **item)
            session.add(code)
        print(f"Seeded {len(hs_data)} HS codes")

        # Seed emission factors
        ef_path = data_dir / "emission_factors.json"
        ef_data = json.loads(ef_path.read_text())
        for item in ef_data:
            factor = EmissionFactor(id=str(uuid.uuid4()), **item)
            session.add(factor)
        print(f"Seeded {len(ef_data)} emission factors")

        await session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
