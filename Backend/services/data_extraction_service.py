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
        """Use LLM to extract structured data using llama-cpp-python chat completion"""
        try:
            # Load model if needed
            self.llm_service._load_model()
            
            # Build the prompt content
            prompt_content = self.EXTRACTION_PROMPT.format(article_text=article_text)
            
            # Use chat format for instruction-tuned models
            # llama-cpp-python handles chat template internally via create_chat_completion
            messages = [
                {"role": "system", "content": "You are a data extraction expert. Your goal is to identify and structure all numerical data, statistical insights, and key performance indicators from the provided news article."},
                {"role": "user", "content": prompt_content}
            ]
            
            # Use llama-cpp-python's create_chat_completion API
            response = self.llm_service.model.create_chat_completion(
                messages=messages,
                max_tokens=2048,  # Increased to prevent JSON truncation
                temperature=0.3,
                top_p=0.9,
                stop=["</s>", "<|eot_id|>", "<|end_of_text|>"]
            )
            
            # Extract generated text from response
            generated_text = response["choices"][0]["message"]["content"].strip()
            
            print(f"Generated text (first 500 chars): {generated_text[:500]}")  # Debug logging
            
            # Extract JSON from response
            json_str = self._extract_json(generated_text)
            if json_str:
                return self._parse_json_response(json_str)
            else:
                print(f"No JSON found in response: {generated_text[:300]}")
            
            return ExtractedData()
            
        except Exception as e:
            print(f"LLM extraction error: {e}")
            import traceback
            traceback.print_exc()
            return ExtractedData()
    
    def _extract_json(self, text: str) -> Optional[str]:
        """Extract JSON object from text, with repair for truncated responses"""
        # Try to find JSON block
        text = text.strip()
        
        # Look for JSON starting with {
        start_idx = text.find('{')
        if start_idx == -1:
            return None
        
        # Find matching closing brace
        brace_count = 0
        bracket_count = 0
        end_idx = start_idx
        last_valid_pos = start_idx
        
        for i, char in enumerate(text[start_idx:], start_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
            elif char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
            
            # Track last position after a complete value
            if char in ',}]':
                last_valid_pos = i + 1
        
        if end_idx > start_idx:
            return text[start_idx:end_idx]
        
        # JSON is truncated - attempt to repair
        if brace_count > 0:
            print(f"JSON appears truncated (unclosed braces: {brace_count}, brackets: {bracket_count}). Attempting repair...")
            json_fragment = text[start_idx:]
            
            # Close any open brackets first, then braces
            repaired = json_fragment.rstrip(',: \n\r\t"')
            
            # If we're mid-string, close the string
            quote_count = repaired.count('"') - repaired.count('\\"')
            if quote_count % 2 == 1:
                repaired += '"'
            
            # Close arrays and objects
            repaired += ']' * bracket_count
            repaired += '}' * brace_count
            
            # Try to validate the repaired JSON
            try:
                json.loads(repaired)
                print("JSON repair successful!")
                return repaired
            except json.JSONDecodeError as e:
                print(f"JSON repair failed: {e}")
                return None
        
        return None
    
    def _parse_json_response(self, json_str: str) -> ExtractedData:
        """Parse JSON string into ExtractedData with robust handling of schema variations"""
        try:
            data = json.loads(json_str)
            
            extracted = ExtractedData()
            
            # Parse comparisons - handle both 'entities' dict and 'value' single value formats
            comparisons_data = data.get('comparisons', [])
            if isinstance(comparisons_data, list):
                for comp in comparisons_data:
                    try:
                        if isinstance(comp, dict) and 'metric' in comp:
                            # Handle 'entities' format: {"Entity A": 10, "Entity B": 20}
                            if 'entities' in comp and isinstance(comp.get('entities'), dict):
                                extracted.comparisons.append(Comparison(
                                    metric=comp.get('metric', ''),
                                    entities=comp.get('entities', {}),
                                    unit=comp.get('unit', ''),
                                    source_snippet=comp.get('source_snippet', '')
                                ))
                            # Handle 'entity1/entity2/value' format from LLM
                            elif 'entity1' in comp and 'entity2' in comp:
                                # Parse value - could be string like "6.84%" or numeric
                                val = comp.get('value', 0)
                                if isinstance(val, str):
                                    # Extract numeric part from strings like "6.84%", "$285 billion"
                                    import re as regex_mod
                                    num_match = regex_mod.search(r'([\d.]+)', val)
                                    val = float(num_match.group(1)) if num_match else 0
                                extracted.comparisons.append(Comparison(
                                    metric=comp.get('metric', ''),
                                    entities={
                                        comp.get('entity1', 'Entity 1'): val,
                                        comp.get('entity2', 'Entity 2'): 0  # Comparison reference
                                    },
                                    unit=comp.get('unit', '') or self._extract_unit(comp.get('value', '')),
                                    source_snippet=comp.get('source_snippet', '')
                                ))
                            # Handle simple 'value' format: {"metric": "...", "value": 15}
                            elif 'value' in comp:
                                extracted.comparisons.append(Comparison(
                                    metric=comp.get('metric', ''),
                                    entities={comp.get('metric', 'Value'): comp.get('value', 0)},
                                    unit=comp.get('unit', ''),
                                    source_snippet=comp.get('source_snippet', '')
                                ))
                    except Exception as e:
                        print(f"Error parsing comparison: {e}")
                        continue
            
            # Parse breakdowns - handle both list and dict formats
            breakdowns_data = data.get('breakdowns', [])
            if isinstance(breakdowns_data, list):
                for bd in breakdowns_data:
                    try:
                        if isinstance(bd, dict) and 'category' in bd and 'values' in bd:
                            extracted.breakdowns.append(Breakdown(
                                category=bd.get('category', ''),
                                values=bd.get('values', {}),
                                unit=bd.get('unit', '%')
                            ))
                    except Exception as e:
                        print(f"Error parsing breakdown: {e}")
                        continue
            elif isinstance(breakdowns_data, dict):
                # Handle dict format: {"total_composition": {"Part A": 50, "Part B": 50}}
                try:
                    for category, values in breakdowns_data.items():
                        if isinstance(values, dict):
                            extracted.breakdowns.append(Breakdown(
                                category=category,
                                values=values,
                                unit='%'
                            ))
                except Exception as e:
                    print(f"Error parsing breakdown dict: {e}")
            
            # Parse time series
            time_series_data = data.get('time_series', [])
            if isinstance(time_series_data, list):
                for ts in time_series_data:
                    try:
                        if isinstance(ts, dict) and 'label' in ts and 'data' in ts:
                            extracted.time_series.append(TimeSeries(
                                label=ts.get('label', ''),
                                data=ts.get('data', []),
                                unit=ts.get('unit', '')
                            ))
                    except Exception as e:
                        print(f"Error parsing time series: {e}")
                        continue
            
            # Parse key facts
            key_facts_data = data.get('key_facts', [])
            if isinstance(key_facts_data, list):
                for kf in key_facts_data:
                    try:
                        if isinstance(kf, dict) and 'fact' in kf and 'value' in kf:
                            extracted.key_facts.append(KeyFact(
                                fact=kf.get('fact', ''),
                                value=str(kf.get('value', '')),
                                context=kf.get('context', '')
                            ))
                    except Exception as e:
                        print(f"Error parsing key fact: {e}")
                        continue
            
            # Parse tables
            extracted.tables = data.get('tables', [])
            
            return extracted
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return ExtractedData()
    
    def _extract_unit(self, value_str: str) -> str:
        """Extract unit from a value string like '6.84%' or '$285 billion'"""
        if not isinstance(value_str, str):
            return ''
        value_str = value_str.strip()
        if '%' in value_str:
            return '%'
        if '$' in value_str or '₹' in value_str:
            # Check for magnitude
            for unit in ['billion', 'million', 'trillion', 'crore', 'lakh']:
                if unit in value_str.lower():
                    return f"$ {unit}"
            return '$'
        for unit in ['billion', 'million', 'trillion', 'crore', 'lakh']:
            if unit in value_str.lower():
                return unit
        return ''
    
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
