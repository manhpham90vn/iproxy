from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.account import User, UserRole
from app.services.auth import hash_password


async def seed_admin():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == settings.admin_username))
        existing = result.scalar_one_or_none()
        if not existing:
            admin = User(
                username=settings.admin_username,
                hashed_password=hash_password(settings.admin_password),
                role=UserRole.admin,
            )
            db.add(admin)
            await db.commit()
            print(f"Admin user created: {settings.admin_username}")
        else:
            print("Admin user already exists")
