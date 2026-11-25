"""État du serveur."""
from fastapi import APIRouter, Request

router = APIRouter(tags=["système"])


@router.get("/health", summary="Le serveur répond-il ?")
def health(request: Request):
    return {"status": "ok", "stockage": request.app.state.stockage}
