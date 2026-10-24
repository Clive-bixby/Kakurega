from pydantic import BaseModel


class UploadImageResponse(BaseModel):
    image_id: str
    path: str
