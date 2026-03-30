import json
from services.gemini_client import GeminiClient
from utils.validator import validate_json_response


class AutomationPlanner:
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    def get_planner_prompt(self):
        return """You are an Automation Planning Agent.
You convert feasibility analysis into detailed, actionable automation plans.

MANDATORY: Return ONLY valid JSON, no additional text.

Response must include these exact fields:
- plan_title: Clear, concise title for the automation
- implementation_approach: String describing the overall approach and architecture
- tool_selection: List of objects with 'tool' and 'justification' fields
- implementation_steps: List of detailed implementation steps (each step is an object with 'step_number', 'description', 'duration_estimate', and 'complexity' (low/medium/high))
- data_flow: String describing how data flows through the automation
- trigger_mechanism: String explaining how the automation will be triggered (schedule, webhook, manual, etc.)
- output_formats: List of output formats the automation will produce
- resource_requirements: Object with 'technical_skills', 'infrastructure', 'api_quotas', 'security_considerations'
- success_criteria: List of measurable success criteria
- estimated_timeline: Object with 'setup_days', 'testing_days', 'deployment_days', 'total_days'
- risk_mitigation: List of objects with 'risk', 'likelihood' (low/medium/high), and 'mitigation_strategy'
- monitoring_strategy: String describing how to monitor the automation
- rollback_plan: String describing rollback procedure if needed
- maintenance_requirements: String describing ongoing maintenance needs

IMPORTANT RULES:
- Be specific and actionable - each step should be implementable
- Consider error handling and edge cases
- Include security considerations (API keys, data protection, etc.)
- Estimate realistic timelines
- Use free and open-source tools only
- Reference tools and APIs from the original analysis if available
- Provide step-by-step implementation clarity for developers

Return ONLY the JSON object, no markdown, no explanation."""
    
    def create_plan(self, workflow, analysis_result):
        """Generate detailed automation plan from analysis result"""
        
        if analysis_result.get('feasibility') == 'NOT_AUTOMATABLE':
            return {
                'error': 'Cannot create plan for non-automatable workflows',
                'message': analysis_result.get('reason', 'This workflow cannot be automated based on the analysis')
            }
        
        system_prompt = self.get_planner_prompt()
        
        context_from_analysis = f"""
Original Workflow: {workflow}

Feasibility Analysis:
- Feasibility Level: {analysis_result.get('feasibility')}
- Reasoning: {analysis_result.get('reason')}
- Recommended Tools: {', '.join(analysis_result.get('recommended_tools', []))}
- Automation Plan (High-level): {', '.join(analysis_result.get('automation_plan', []))}
- Constraints: {', '.join(analysis_result.get('constraints', []))}

Create a detailed, structured plan to implement this automation based on the analysis above."""
        
        prompt = f"""Based on this automation analysis, create a detailed implementation plan:

{context_from_analysis}

Return only the JSON response with all required fields."""
        
        headers = {
            "Authorization": f"Bearer {self.gemini_client.api_key}",
            "Content-Type": "application/json"
        }
        
        import requests
        
        payload = {
            "model": self.gemini_client.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }
        
        response = requests.post(self.gemini_client.api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        raw_response = result["choices"][0]["message"]["content"]
        
        try:
            validated_plan = self._validate_plan_response(raw_response)
            return validated_plan
        except ValueError as e:
            return {
                'error': 'Plan validation failed',
                'message': str(e),
                'raw_response': raw_response
            }
    
    def _validate_plan_response(self, response_text):
        """Validate plan response structure"""
        import re
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if not json_match:
                raise ValueError("No JSON object found in response")
            
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            required_fields = [
                'plan_title', 'implementation_approach', 'tool_selection',
                'implementation_steps', 'data_flow', 'trigger_mechanism',
                'output_formats', 'resource_requirements', 'success_criteria',
                'estimated_timeline', 'risk_mitigation', 'monitoring_strategy',
                'rollback_plan', 'maintenance_requirements'
            ]
            
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            return data
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")
