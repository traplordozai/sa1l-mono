from fastapi import APIRouter
from .schemas import MatchInput, MatchResult

router = APIRouter()

@router.post("/match", response_model=MatchResult)
def run_match(data: MatchInput):
    return MatchResult(match_id=1, status="ok")