import sqlite3
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Path, Query, status

from labs.lab03 import repository
from labs.lab03.config import VALUE_MAX, VALUE_MIN
from labs.lab03.schemas import RecordCreate, RecordRead, RecordReplace

router = APIRouter(prefix="/records", tags=["Records"])


@router.get("", response_model=List[RecordRead])
def get_records(
    category_id: Optional[int] = Query(None, gt=0),
    status_param: Optional[str] = Query(None, alias="status"),
    min_value: Optional[float] = Query(None, ge=VALUE_MIN, le=VALUE_MAX),
    q: Optional[str] = Query(None, min_length=1, max_length=120),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[RecordRead]:
    if category_id is not None:
        cat = repository.get_category_by_id(category_id)
        if not cat:
            return []

    return repository.get_records(
        category_id=category_id,
        status=status_param,
        min_value=min_value,
        q=q,
        limit=limit,
        offset=offset,
    )


@router.get("/{record_id}", response_model=RecordRead)
def get_record(
    record_id: int = Path(..., gt=0, description="Ідентифікатор запису"),
) -> RecordRead:
    record = repository.get_record_by_id(record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запис з id={record_id} не знайдено",
        )
    return record


@router.post("", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
def create_record(record: RecordCreate) -> RecordRead:
    cat = repository.get_category_by_id(record.category_id)
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Категорію з id={record.category_id} не знайдено",
        )

    try:
        return repository.create_record(record.model_dump())
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Конфлікт унікальності або даних: {e}",
        )


@router.put("/{record_id}", response_model=RecordRead)
def update_record(
    record_data: RecordReplace,
    record_id: int = Path(..., gt=0, description="Ідентифікатор запису"),
) -> RecordRead:
    cat = repository.get_category_by_id(record_data.category_id)
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Категорію з id={record_data.category_id} не знайдено",
        )

    try:
        updated = repository.update_record(record_id, record_data.model_dump())
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Запис з id={record_id} не знайдено",
            )
        return updated
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Конфлікт унікальності даних: {e}",
        )


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int = Path(..., gt=0, description="Ідентифікатор запису"),
) -> None:
    deleted = repository.delete_record(record_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запис з id={record_id} не знайдено",
        )


@router.post(
    "/bulk", response_model=List[RecordRead], status_code=status.HTTP_201_CREATED
)
def create_records_bulk(records: List[RecordCreate]) -> List[RecordRead]:
    if not (1 <= len(records) <= 100):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Кількість елементів у пакеті повинна бути від 1 до 100",
        )

    codes = [r.code for r in records]
    if len(codes) != len(set(codes)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="У надісланому пакеті присутні дублікати поля 'code'",
        )

    for r in records:
        if not repository.get_category_by_id(r.category_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категорію з id={r.category_id} не знайдено",
            )

    try:
        return repository.create_records_bulk([r.model_dump() for r in records])
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Транзакцію скасовано через конфлікт у базі: {e}",
        )
