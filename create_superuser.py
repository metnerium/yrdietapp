import asyncio
import asyncpg
from urllib.parse import urlparse
from config import DATABASE_URL, FIRST_SUPERUSER_USERNAME, FIRST_SUPERUSER_PASSWORD
from app.utils.security import get_password_hash

def get_db_url(url):
    parsed = urlparse(url)
    return f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}/{parsed.path[1:]}"

async def create_superuser():
    db_url = get_db_url(DATABASE_URL)
    conn = await asyncpg.connect(db_url)

    # Проверяем, существует ли таблица admins
    table_exists = await conn.fetchval(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'admins')"
    )

    if not table_exists:
        # Создаем таблицу admins, если она не существует
        await conn.execute('''
            CREATE TABLE admins (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                hashed_password VARCHAR(100) NOT NULL,
                is_superadmin BOOLEAN NOT NULL DEFAULT FALSE
            )
        ''')

    # Проверяем, существует ли уже суперпользователь
    existing_admin = await conn.fetchrow(
        "SELECT * FROM admins WHERE username = $1",
        FIRST_SUPERUSER_USERNAME
    )

    if existing_admin:
        print(f"Суперпользователь с именем {FIRST_SUPERUSER_USERNAME} уже существует.")
    else:
        # Создаем нового суперпользователя
        hashed_password = get_password_hash(FIRST_SUPERUSER_PASSWORD)
        await conn.execute('''
            INSERT INTO admins (username, hashed_password, is_superadmin)
            VALUES ($1, $2, $3)
        ''', FIRST_SUPERUSER_USERNAME, hashed_password, True)
        print(f"Суперпользователь {FIRST_SUPERUSER_USERNAME} успешно создан.")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(create_superuser())