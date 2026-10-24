from pydantic import BaseModel


class BarcodeResponse(BaseModel):
    isbn: str
