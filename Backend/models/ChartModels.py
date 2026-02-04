"""
Chart Request/Response Models
Pydantic models for chart extraction and generation API
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ExtractRequest(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None


class ExtractResponse(BaseModel):
    success: bool
    extracted_data: Dict[str, Any]
    data_preview: List[Dict[str, Any]]
    message: str


class GenerateRequest(BaseModel):
    extracted_data: Dict[str, Any]
    chart_types: Optional[List[str]] = None


class ChartOutput(BaseModel):
    png_base64: str
    chart_type: str
    caption: str
    alt_text: str
    data_summary: str


class GenerateResponse(BaseModel):
    success: bool
    charts: List[ChartOutput]
    message: str


class FullPipelineRequest(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None
    chart_types: Optional[List[str]] = None


class FullPipelineResponse(BaseModel):
    success: bool
    extracted_data: Dict[str, Any]
    charts: List[ChartOutput]
    message: str

@dataclass
class ChartResult:
    """Container for generated chart"""
    png_base64: str
    chart_type: str
    caption: str
    alt_text: str
    data_summary: str