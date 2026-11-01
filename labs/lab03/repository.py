import sqlite3
from typing import Any, Dict, List, Optional
from labs.lab03.database import get_connection


def get_all_categories() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT id, name FROM categories ORDER BY id ASC")
        rows = cursor.fetchall()
        return [{"id": r[0], "name": r[1]} for r in rows]


def get_category_by_id(category_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, name FROM categories WHERE id = ?", (category_id,)
        )
        row = cursor.fetchone()
        return {"id": row[0], "name": row[1]} if row else None


def create_category(name: str) -> Dict[str, Any]:
    conn = get_connection()
    try:
        with conn:
            cursor = conn.execute(
                "INSERT INTO categories (name) VALUES (?) RETURNING id, name",
                (name,),
            )
            row = cursor.fetchone()
            return {"id": row[0], "name": row[1]}
    finally:
        conn.close()


def delete_category(category_id: int) -> bool:
    conn = get_connection()
    try:
        with conn:
            cursor = conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()


def get_record_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT r.id, r.code, r.title, r.category_id, c.name AS category_name, r.value, r.status
            FROM records r
            JOIN categories c ON r.category_id = c.id
            WHERE r.id = ?
            """,
            (record_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "code": row[1],
            "title": row[2],
            "category_id": row[3],
            "category_name": row[4],
            "value": row[5],
            "status": row[6],
        }


def get_records(
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    min_value: Optional[float] = None,
    q: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    conditions = []
    params: List[Any] = []

    if category_id is not None:
        conditions.append("r.category_id = ?")
        params.append(category_id)

    if status is not None:
        conditions.append("r.status = ?")
        params.append(status)

    if min_value is not None:
        conditions.append("r.value >= ?")
        params.append(min_value)

    if q is not None:
        conditions.append("instr(r.title, ?) > 0")
        params.append(q)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    sql = f"""
        SELECT r.id, r.code, r.title, r.category_id, c.name AS category_name, r.value, r.status
        FROM records r
        JOIN categories c ON r.category_id = c.id
        {where_clause}
        ORDER BY r.id ASC
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()
        return [
            {
                "id": r[0],
                "code": r[1],
                "title": r[2],
                "category_id": r[3],
                "category_name": r[4],
                "value": r[5],
                "status": r[6],
            }
            for r in rows
        ]


def create_record(data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO records (code, title, category_id, value, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    data["code"],
                    data["title"],
                    data["category_id"],
                    data["value"],
                    data["status"],
                ),
            )
            new_id = cursor.lastrowid
        return get_record_by_id(new_id)  # type: ignore
    finally:
        conn.close()


def update_record(record_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        with conn:
            cursor = conn.execute(
                """
                UPDATE records
                SET code = ?, title = ?, category_id = ?, value = ?, status = ?
                WHERE id = ?
                """,
                (
                    data["code"],
                    data["title"],
                    data["category_id"],
                    data["value"],
                    data["status"],
                    record_id,
                ),
            )
            if cursor.rowcount == 0:
                return None
        return get_record_by_id(record_id)
    finally:
        conn.close()


def delete_record(record_id: int) -> bool:
    conn = get_connection()
    try:
        with conn:
            cursor = conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()


def create_records_bulk(records_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    conn = get_connection()
    inserted_ids = []
    try:
        with conn:
            for item in records_data:
                cursor = conn.execute(
                    """
                    INSERT INTO records (code, title, category_id, value, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        item["code"],
                        item["title"],
                        item["category_id"],
                        item["value"],
                        item["status"],
                    ),
                )
                inserted_ids.append(cursor.lastrowid)

        result = []
        for rid in inserted_ids:
            rec = get_record_by_id(rid)
            if rec:
                result.append(rec)
        return result
    finally:
        conn.close()
