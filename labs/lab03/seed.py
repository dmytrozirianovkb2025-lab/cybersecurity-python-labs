import json
import logging
import sqlite3
from pathlib import Path
from labs.lab03.database import get_connection, initialize_database

BASE_DIR = Path(__file__).resolve().parent
SEED_JSON_PATH = BASE_DIR / "data" / "seed.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database() -> None:
    initialize_database()

    if not SEED_JSON_PATH.exists():
        logger.error(f"Файл початкових даних не знайдено: {SEED_JSON_PATH}")
        return

    with SEED_JSON_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    categories = data.get("categories", [])
    records = data.get("records", [])

    connection = get_connection()
    try:
        with connection:
            cursor = connection.execute("SELECT COUNT(*) FROM categories")
            count = cursor.fetchone()[0]
            if count > 0:
                logger.info("База даних вже містить дані. Заповнення скасовано.")
                return

            for cat in categories:
                connection.execute(
                    "INSERT INTO categories (id, name) VALUES (?, ?)",
                    (cat["id"], cat["name"]),
                )

            for rec in records:
                connection.execute(
                    """
                    INSERT INTO records (code, title, category_id, value, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        rec["code"],
                        rec["title"],
                        rec["category_id"],
                        rec["value"],
                        rec["status"],
                    ),
                )
        logger.info("Базу даних успішно заповнено початковими даними!")
    except sqlite3.IntegrityError as e:
        logger.error(
            f"Помилка цілісності даних при заповненні (Transaction rollback): {e}"
        )
    except sqlite3.Error as e:
        logger.error(f"Помилка бази даних: {e}")
    finally:
        connection.close()


if __name__ == "__main__":
    seed_database()
