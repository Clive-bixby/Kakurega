from fastapi import APIRouter

from app.api.v1.routes.barcode import router as barcode_router
from app.api.v1.routes.books import router as books_router
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.importing import router as importing_router
from app.api.v1.routes.insights import router as insights_router
from app.api.v1.routes.lookup import router as lookup_router
from app.api.v1.routes.taxonomy import router as taxonomy_router
from app.api.v1.routes.upload import router as upload_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(insights_router, prefix="/insights", tags=["insights"])
api_router.include_router(barcode_router, prefix="/barcode", tags=["barcode"])
api_router.include_router(books_router, prefix="/books", tags=["books"])
api_router.include_router(importing_router, prefix="/import", tags=["import"])
api_router.include_router(lookup_router, prefix="/lookup", tags=["lookup"])
api_router.include_router(taxonomy_router, tags=["taxonomy"])
api_router.include_router(upload_router, prefix="/upload", tags=["upload"])
