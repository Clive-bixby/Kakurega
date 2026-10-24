from pydantic import BaseModel


class ImportProblem(BaseModel):
    row: int
    reason: str


class ImportResult(BaseModel):
    created: int
    updated: int
    skipped_duplicates: int
    failed: list[ImportProblem]
    warnings: list[ImportProblem]
    ignored_columns: list[str]
