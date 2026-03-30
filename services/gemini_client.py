import os
import requests
import json


class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "openai/gpt-4o-mini"
    
    def get_system_prompt(self):
        return """You are an Automation Feasibility and Workflow Planning Agent.
You analyze tasks using BOTH user input and provided real-world context.
The context represents recent public information and must be respected.

MANDATORY: Return ONLY valid JSON, no additional text.

For the feasibility field, use EXACTLY one of these values (with underscores):
- FULLY_AUTOMATABLE
- PARTIALLY_AUTOMATABLE
- NOT_AUTOMATABLE

Response must include these exact fields:
- task_summary: Brief summary of the task
- feasibility: One of the three values above
- reason: Why it has this feasibility level (consider live context)
- live_context_used: List of key context points that influenced your decision
- assumptions: List of assumptions you made
- constraints: List of constraints and risks (include any from live context)
- alternative_suggestions: List of alternatives if not fully automatable
- recommended_tools: List of free/open-source tools (prioritize APIs found in context)
- automation_plan: List of step-by-step automation plan
- manual_work_reduction: Explanation of how much manual work would be reduced
- validation_and_monitoring: List of validation and monitoring suggestions

IMPORTANT RULES:
- If live context suggests blocking or instability, downgrade feasibility
- If APIs or feeds are found in context, prefer them over scraping
- If no live signals are found, clearly state uncertainty
- Never assume access without evidence from context
- Never hallucinate APIs not mentioned in context

Return ONLY the JSON object, no markdown, no explanation."""
    
    def analyze_workflow(self, workflow, live_context=""):
        system_prompt = self.get_system_prompt()
        
        context_section = ""
        if live_context.strip():
            context_section = f"""

LIVE CONTEXT DATA (Recent public information):
{live_context}

Use this context to inform your feasibility assessment. If context suggests issues, reflect that in your analysis."""

        prompt = f"""Analyze this workflow for automation feasibility:

{workflow}{context_section}

Return only the JSON response with all required fields."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
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
        
        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
