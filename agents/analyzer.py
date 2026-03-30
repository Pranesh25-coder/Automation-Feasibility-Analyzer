from services.gemini_client import GeminiClient
from services.web_context_fetcher import WebContextFetcher
from utils.validator import validate_json_response


class AutomationAnalyzer:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.web_fetcher = WebContextFetcher()
    
    def analyze(self, workflow):
        # Step 1: Fetch live context data
        print(f"Fetching live context for workflow...")
        live_context_data = self.web_fetcher.fetch_live_context(workflow)
        
        # Step 2: Format context for Gemini
        formatted_context = self.web_fetcher.format_context_for_gemini(live_context_data)
        print(f"Live context summary: {len(formatted_context)} characters")
        
        # Step 3: Analyze workflow with Gemini using live context
        raw_response = self.gemini_client.analyze_workflow(workflow, formatted_context)
        
        # Step 4: Validate and return response
        validated_response = validate_json_response(raw_response)
        
        # Step 5: Ensure live_context_used field is populated
        if 'live_context_used' not in validated_response or not validated_response['live_context_used']:
            validated_response['live_context_used'] = self._extract_context_summary(live_context_data)
        
        return validated_response
    
    def _extract_context_summary(self, live_context_data):
        """Extract key points from live context data for the response"""
        summary = []
        
        if live_context_data['api_availability']:
            summary.append("Found API/feed options")
        
        if live_context_data['blocking_reports']:
            summary.append("Found blocking/access issue reports")
        
        if live_context_data['alternatives_found']:
            summary.append("Found alternative approaches")
        
        if live_context_data['search_queries_performed']:
            summary.append(f"Performed {len(live_context_data['search_queries_performed'])} live searches")
        
        if not summary:
            summary.append("No specific live context signals found")
        
        return summary
