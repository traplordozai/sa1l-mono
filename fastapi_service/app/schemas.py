from pydantic import BaseModel

class MatchInput(BaseModel):
    student_ids: list[int]
    round_id: int

class MatchResult(BaseModel):
    match_id: int
    status: str