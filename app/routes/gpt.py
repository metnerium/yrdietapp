from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.rest.message_handler import send_diet, send_post
from app.mappers.text_mapper import extract_text_from_response
from app.dependencies import get_current_user_dependency
from app.models.user import User

router = APIRouter()

class MessageRequest(BaseModel):
    message: str

@router.post("/diet")
async def diet(request: MessageRequest, current_user: User = Depends(get_current_user_dependency)):
    try:
        response = send_diet(request.message)
        answer = extract_text_from_response(response)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/rewrite")
async def rewriter(request: MessageRequest, current_user: User = Depends(get_current_user_dependency)):
    try:
        response = send_post(request.message)
        answer = extract_text_from_response(response)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))