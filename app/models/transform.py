from pydantic import BaseModel
from typing import Any, Optional


class TransformRequest(BaseModel):
    input_json: dict[str, Any]
    jslt_expression: str


class TransformResponse(BaseModel):
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float


class JSLTValidationRequest(BaseModel):
    jslt_expression: str


class JSLTValidationResponse(BaseModel):
    valid: bool
    error: Optional[str] = None
    suggestions: list[str] = []