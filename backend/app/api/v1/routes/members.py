from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.errors import DuplicateMemberError
from app.schemas.reading import MemberCreate, MemberRead, MemberUpdate
from app.services.reading import ReadingService

router = APIRouter()


@router.get("", response_model=list[MemberRead])
def list_members(db: Session = Depends(get_db)):
    return ReadingService(db).list_members()


@router.post("", response_model=MemberRead, status_code=201)
def create_member(data: MemberCreate, db: Session = Depends(get_db)):
    try:
        return ReadingService(db).create_member(data)
    except DuplicateMemberError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.patch("/{member_id}", response_model=MemberRead)
def update_member(
    member_id: int, data: MemberUpdate, db: Session = Depends(get_db)
):
    try:
        member = ReadingService(db).update_member(member_id, data)
    except DuplicateMemberError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.delete("/{member_id}", status_code=204)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    if not ReadingService(db).delete_member(member_id):
        raise HTTPException(status_code=404, detail="Member not found")
    return None
