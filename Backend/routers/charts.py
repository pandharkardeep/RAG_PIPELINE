from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
import base64
import io
import zipfile

from services.data_extraction_service import DataExtractionService, ExtractedData
from services.chart_service import ChartService, ChartResult
from models.ChartModels import (
    ExtractRequest, ExtractResponse, GenerateRequest, 
    ChartOutput, GenerateResponse, FullPipelineRequest, FullPipelineResponse
)


router = APIRouter(prefix="/charts", tags=["Charts"])

# Initialize services
data_extraction_service = DataExtractionService()
chart_service = ChartService()


@router.post("/extract", response_model=ExtractResponse)
async def extract_data(request: ExtractRequest):
    """
    Extract structured data from article text or URL
    
    - **text**: Article text to analyze
    - **url**: URL to fetch and analyze (if text not provided)
    """
    try:
        if not request.text and not request.url:
            raise HTTPException(status_code=400, detail="Either text or url must be provided")
        
        # Extract data
        if request.text:
            extracted = data_extraction_service.extract_from_text(request.text)
        else:
            extracted = data_extraction_service.extract_from_url(request.url)
        
        # Convert to dict for response
        data_dict = extracted.to_dict()
        
        # Create preview for UI display
        preview = []
        
        for comp in extracted.comparisons:
            preview.append({
                "type": "comparison",
                "metric": comp.metric,
                "data": comp.entities,
                "unit": comp.unit
            })
        
        for bd in extracted.breakdowns:
            preview.append({
                "type": "breakdown", 
                "category": bd.category,
                "data": bd.values,
                "unit": bd.unit
            })
        
        for ts in extracted.time_series:
            preview.append({
                "type": "time_series",
                "label": ts.label,
                "data": ts.data,
                "unit": ts.unit
            })
        
        for kf in extracted.key_facts:
            preview.append({
                "type": "key_fact",
                "fact": kf.fact,
                "value": kf.value,
                "context": kf.context
            })
        
        is_empty = extracted.is_empty()
        
        return ExtractResponse(
            success=not is_empty,
            extracted_data=data_dict,
            data_preview=preview,
            message="Data extracted successfully" if not is_empty else "No data could be extracted from the provided text"
        )
        
    except Exception as e:
        print(f"Extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=GenerateResponse)
async def generate_charts(request: GenerateRequest):
    """
    Generate charts from extracted data
    
    - **extracted_data**: Data dictionary from /extract endpoint
    - **chart_types**: Optional list of chart types to generate
    """
    try:
        data = request.extracted_data
        
        if not data:
            raise HTTPException(status_code=400, detail="extracted_data is required")
        
        charts = []
        
        if request.chart_types:
            # Generate specific chart types
            for chart_type in request.chart_types:
                result = chart_service.generate_chart(data, chart_type)
                charts.append(ChartOutput(
                    png_base64=result.png_base64,
                    chart_type=result.chart_type,
                    caption=result.caption,
                    alt_text=result.alt_text,
                    data_summary=result.data_summary,
                    source_data=result.source_data
                ))
        else:
            # Auto-generate all applicable charts
            results = chart_service.generate_all_charts(data)
            for result in results:
                charts.append(ChartOutput(
                    png_base64=result.png_base64,
                    chart_type=result.chart_type,
                    caption=result.caption,
                    alt_text=result.alt_text,
                    data_summary=result.data_summary,
                    source_data=result.source_data
                ))
        
        return GenerateResponse(
            success=len(charts) > 0,
            charts=charts,
            message=f"Generated {len(charts)} chart(s)" if charts else "No charts could be generated"
        )
        
    except Exception as e:
        print(f"Chart generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/full-pipeline", response_model=FullPipelineResponse)
async def full_pipeline(request: FullPipelineRequest):
    """
    End-to-end extraction and chart generation
    
    - **text**: Article text to analyze
    - **url**: URL to fetch and analyze (if text not provided)
    - **chart_types**: Optional list of specific chart types
    """
    try:
        if not request.text and not request.url:
            raise HTTPException(status_code=400, detail="Either text or url must be provided")
        
        # Step 1: Extract data
        if request.text:
            extracted = data_extraction_service.extract_from_text(request.text)
        else:
            extracted = data_extraction_service.extract_from_url(request.url)
        
        data_dict = extracted.to_dict()
        
        if extracted.is_empty():
            return FullPipelineResponse(
                success=False,
                extracted_data=data_dict,
                charts=[],
                message="No data could be extracted from the provided text"
            )
        
        # Step 2: Generate charts
        charts = []
        
        if request.chart_types:
            for chart_type in request.chart_types:
                result = chart_service.generate_chart(data_dict, chart_type)
                charts.append(ChartOutput(
                    png_base64=result.png_base64,
                    chart_type=result.chart_type,
                    caption=result.caption,
                    alt_text=result.alt_text,
                    data_summary=result.data_summary,
                    source_data=result.source_data
                ))
        else:
            results = chart_service.generate_all_charts(data_dict)
            for result in results:
                charts.append(ChartOutput(
                    png_base64=result.png_base64,
                    chart_type=result.chart_type,
                    caption=result.caption,
                    alt_text=result.alt_text,
                    data_summary=result.data_summary,
                    source_data=result.source_data
                ))
        
        return FullPipelineResponse(
            success=True,
            extracted_data=data_dict,
            charts=charts,
            message=f"Extracted data and generated {len(charts)} chart(s)"
        )
        
    except Exception as e:
        print(f"Full pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chart-types")
async def get_chart_types():
    """Get available chart types"""
    return {
        "chart_types": [
            {"id": "bar", "name": "Vertical Bar Chart", "description": "Best for comparing categories"},
            {"id": "horizontal_bar", "name": "Horizontal Bar Chart", "description": "Best for 2-6 category comparisons"},
            {"id": "pie", "name": "Pie/Donut Chart", "description": "Best for percentage breakdowns (~100%)"},
            {"id": "line", "name": "Line Chart", "description": "Best for time series data"},
            {"id": "big_number", "name": "Big Number Infographic", "description": "Best for key statistics"},
            {"id": "grouped_bar", "name": "Grouped Bar Chart", "description": "Best for multi-metric comparisons"}
        ]
    }
