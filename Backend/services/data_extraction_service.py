"""
Data Extraction Service
Extracts structured numerical data from article text using LLM with JSON schema
"""

import re
import json
from typing import Optional
import pandas as pd
import trafilatura
from services.llm_service import LLMService
from models.DataModels import ExtractedData, Comparison, Breakdown, TimeSeries, KeyFact


class DataExtractionService:
    """
    Service for extracting structured data from articles using LLM
    """
    
    EXTRACTION_PROMPT = """You are a data extraction expert. Your goal is to identify and structure all numerical data, statistical insights, and key performance indicators from the provided news article.

ARTICLE TEXT:
{article_text}

OUTPUT INSTRUCTIONS:
Return ONLY a valid JSON object with the following structure. Do not include markdown formatting, preamble, or explanations:
{{
  "comparisons": [
    {{"metric": "metric name", "entities": {{"Entity A": 10, "Entity B": 20}}, "unit": "unit", "source_snippet": "text snippet"}}
  ],
  "breakdowns": [
    {{"category": "total composition", "values": {{"Part A": 50, "Part B": 50}}, "unit": "%"}}
  ],
  "time_series": [
    {{"label": "trend name", "data": [{{"year": 2022, "value": 100}}], "unit": "currency/unit"}}
  ],
  "key_facts": [
    {{"fact": "description", "value": "specific value", "context": "additional info"}}
  ],
  "tables": []
}}

RULES:
- Extract all significant figures, percentages, and monetary values explicitly stated in the text.
- If data for a specific category is not found, return an empty array [].
- Comparisons must involve two or more entities with comparable numeric values.
- Breakdowns must represent parts of a whole or categorical distributions.
- Key facts are for standalone statistics or important data points that do not fit into comparisons or trends.
- Ensure all JSON keys match the template exactly."""

    def __init__(self):
        self.llm_service = LLMService()
        print("DataExtractionService initialized")
    
    def extract_from_text(self, article_text: str) -> ExtractedData:
        """
        Extract structured data from article text using LLM
        
        Args:
            article_text: The article content to analyze
            
        Returns:
            ExtractedData object with extracted information
        """
        if not article_text or not article_text.strip():
            return ExtractedData()
        
        # Try LLM extraction first
        extracted = self._llm_extract(article_text)
        
        # If LLM extraction yields little data, supplement with regex
        if extracted.is_empty():
            print("LLM extraction returned empty, trying regex fallback...")
            extracted = self._regex_fallback(article_text)
        
        extracted.raw_text = article_text[:2000]  # Store truncated original
        return extracted
    
    def extract_from_url(self, url: str) -> ExtractedData:
        """
        Fetch article content from URL and extract data
        
        Args:
            url: The URL to fetch and analyze
            
        Returns:
            ExtractedData object with extracted information
        """
        try:
            # Use trafilatura to fetch and extract main content
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                print(f"Failed to fetch URL: {url}")
                return ExtractedData(source_url=url)
            
            article_text = trafilatura.extract(downloaded)
            if not article_text:
                print(f"Failed to extract content from URL: {url}")
                return ExtractedData(source_url=url)
            
            extracted = self.extract_from_text(article_text)
            extracted.source_url = url
            return extracted
            
        except Exception as e:
            print(f"Error extracting from URL {url}: {e}")
            return ExtractedData(source_url=url)
    
    def _llm_extract(self, article_text: str) -> ExtractedData:
        """Use LLM to extract structured data"""
        try:
            # Load model if needed
            self.llm_service._load_model()
            
            # Build prompt
            prompt = self.EXTRACTION_PROMPT.format(article_text=article_text[:8000])
            
            # Generate using the LLM
            inputs = self.llm_service.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=4096
            ).to(self.llm_service.device)
            
            import torch
            with torch.no_grad():
                outputs = self.llm_service.model.generate(
                    **inputs,
                    max_new_tokens=2048,
                    temperature=0.3,  # Lower temperature for more deterministic output
                    top_p=0.9,
                    do_sample=True,
                    num_return_sequences=1,
                    pad_token_id=self.llm_service.tokenizer.eos_token_id
                )
            
            generated_text = self.llm_service.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract JSON from response
            json_str = self._extract_json(generated_text[len(prompt):])
            if json_str:
                return self._parse_json_response(json_str)
            
            return ExtractedData()
            
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return ExtractedData()
    
    def _extract_json(self, text: str) -> Optional[str]:
        """Extract JSON object from text"""
        # Try to find JSON block
        text = text.strip()
        
        # Look for JSON starting with {
        start_idx = text.find('{')
        if start_idx == -1:
            return None
        
        # Find matching closing brace
        brace_count = 0
        end_idx = start_idx
        for i, char in enumerate(text[start_idx:], start_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        if end_idx > start_idx:
            return text[start_idx:end_idx]
        return None
    
    def _parse_json_response(self, json_str: str) -> ExtractedData:
        """Parse JSON string into ExtractedData"""
        try:
            data = json.loads(json_str)
            
            extracted = ExtractedData()
            
            # Parse comparisons
            for comp in data.get('comparisons', []):
                if isinstance(comp, dict) and 'metric' in comp and 'entities' in comp:
                    extracted.comparisons.append(Comparison(
                        metric=comp.get('metric', ''),
                        entities=comp.get('entities', {}),
                        unit=comp.get('unit', ''),
                        source_snippet=comp.get('source_snippet', '')
                    ))
            
            # Parse breakdowns
            for bd in data.get('breakdowns', []):
                if isinstance(bd, dict) and 'category' in bd and 'values' in bd:
                    extracted.breakdowns.append(Breakdown(
                        category=bd.get('category', ''),
                        values=bd.get('values', {}),
                        unit=bd.get('unit', '%')
                    ))
            
            # Parse time series
            for ts in data.get('time_series', []):
                if isinstance(ts, dict) and 'label' in ts and 'data' in ts:
                    extracted.time_series.append(TimeSeries(
                        label=ts.get('label', ''),
                        data=ts.get('data', []),
                        unit=ts.get('unit', '')
                    ))
            
            # Parse key facts
            for kf in data.get('key_facts', []):
                if isinstance(kf, dict) and 'fact' in kf and 'value' in kf:
                    extracted.key_facts.append(KeyFact(
                        fact=kf.get('fact', ''),
                        value=str(kf.get('value', '')),
                        context=kf.get('context', '')
                    ))
            
            # Parse tables
            extracted.tables = data.get('tables', [])
            
            return extracted
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return ExtractedData()
    
    def _regex_fallback(self, article_text: str) -> ExtractedData:
        """Fallback regex-based extraction when LLM fails"""
        extracted = ExtractedData()
        
        # Pattern: "X: Y%" or "X at Y%"
        comparison_pattern = r'(\w+(?:\s+\w+)?)\s*(?::|at|is|was)\s*~?(\d+(?:\.\d+)?)\s*%'
        matches = re.findall(comparison_pattern, article_text, re.IGNORECASE)
        
        if len(matches) >= 2:
            entities = {match[0].strip(): float(match[1]) for match in matches[:6]}
            extracted.comparisons.append(Comparison(
                metric="Extracted percentage comparison",
                entities=entities,
                unit="%"
            ))
        
        # Pattern: Large numbers with context (e.g., "63.4 million MSMEs")
        large_number_pattern = r'(\d+(?:\.\d+)?)\s*(million|billion|trillion|lakh|crore)\s+(\w+(?:\s+\w+)?)'
        number_matches = re.findall(large_number_pattern, article_text, re.IGNORECASE)
        
        for match in number_matches[:5]:
            extracted.key_facts.append(KeyFact(
                fact=match[2].strip(),
                value=f"{match[0]} {match[1]}",
                context=""
            ))
        
        # Pattern: Year-based values (e.g., "in 2020: $123M" or "2020 saw 45%")
        year_pattern = r'(?:in\s+)?(\d{4})\s*(?::|saw|recorded|was)?\s*[$₹]?(\d+(?:\.\d+)?)\s*(%|million|billion|M|B)?'
        year_matches = re.findall(year_pattern, article_text)
        
        if len(year_matches) >= 2:
            data = [{"year": int(m[0]), "value": float(m[1])} for m in year_matches[:10]]
            extracted.time_series.append(TimeSeries(
                label="Extracted time series",
                data=data,
                unit=year_matches[0][2] if year_matches[0][2] else ""
            ))
        
        return extracted
    
    def extract_html_tables(self, html_content: str) -> list:
        """Extract tables from HTML using pandas"""
        try:
            tables = pd.read_html(html_content)
            return [table.to_dict('records') for table in tables]
        except Exception as e:
            print(f"HTML table extraction error: {e}")
            return []
