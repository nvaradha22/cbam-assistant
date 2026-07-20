"""
Seed script — run once after alembic upgrade head:
  python -m app.seed
"""
import asyncio
import json
import uuid
import os
from pathlib import Path

import asyncpg


def get_dsn() -> str:
    url = os.environ.get("DATABASE_URL", "")
    return url.replace("postgresql+asyncpg://", "postgresql://")


async def seed() -> None:
    data_dir = Path(__file__).parent / "data"
    dsn = get_dsn()

    conn = await asyncpg.connect(dsn, statement_cache_size=0)
    try:
        await conn.execute("DELETE FROM emission_factors")
        await conn.execute("DELETE FROM hs_codes")

        # Seed HS codes
        hs_data = json.loads((data_dir / "hs_codes.json").read_text())
        for item in hs_data:
            await conn.execute(
                """
                INSERT INTO hs_codes (id, cn_code, description, sector, cbam_applicable, reporting_notes)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                str(uuid.uuid4()),
                item["cn_code"],
                item["description"],
                item["sector"],
                item.get("cbam_applicable", True),
                item.get("reporting_notes"),
            )
        print(f"Seeded {len(hs_data)} HS codes")

        # Seed emission factors
        ef_data = json.loads((data_dir / "emission_factors.json").read_text())
        for item in ef_data:
            await conn.execute(
                """
                INSERT INTO emission_factors (id, category, name, country_code, factor_value, unit, source, valid_from, valid_to)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                str(uuid.uuid4()),
                item["category"],
                item["name"],
                item.get("country_code"),
                float(item["factor_value"]),
                item["unit"],
                item.get("source"),
                item.get("valid_from"),
                item.get("valid_to"),
            )
        print(f"Seeded {len(ef_data)} emission factors")

        print("Seed complete.")
    finally:
        await conn.close()


if __name__ == "__main__":
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    asyncio.run(seed())
