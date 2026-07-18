from fastapi import APIRouter, HTTPException

from app.investigation.packs import get_pack, list_packs
from app.schemas.pack import InvestigationPack

router = APIRouter(prefix="/investigation-packs", tags=["investigation-packs"])


@router.get("", response_model=list[InvestigationPack])
def all_packs() -> list[InvestigationPack]:
    return list_packs()


@router.get("/{pack_id}", response_model=InvestigationPack)
def one_pack(pack_id: str) -> InvestigationPack:
    try:
        return get_pack(pack_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
