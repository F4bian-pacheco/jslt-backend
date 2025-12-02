from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.models.transform import (
    TransformRequest,
    TransformResponse,
    JSLTValidationRequest,
    JSLTValidationResponse
)
from app.services.jslt import JSLTService

router = APIRouter()
jslt_service = JSLTService()
limiter = Limiter(key_func=get_remote_address)


@router.post("/transform", response_model=TransformResponse)
#@limiter.limit("10/minute")
async def transform_json(transform_request: TransformRequest):
    try:
        result = jslt_service.transform(transform_request.input_json, transform_request.jslt_expression)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=JSLTValidationResponse)
#@limiter.limit("20/minute")
async def validate_jslt(validation_request: JSLTValidationRequest):
    try:
        result = jslt_service.validate_jslt(validation_request.jslt_expression)
        if not result.valid:
            raise HTTPException(status_code=400, detail=result.error)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
#@limiter.limit("60/minute")
async def health_check():
    return {"status": "healthy", "service": "JSLT Playground API"}