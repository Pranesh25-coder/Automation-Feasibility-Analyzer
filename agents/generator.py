import json
import re
from services.gemini_client import GeminiClient


class AutomationGenerator:
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    def get_generator_prompt(self):
        return """You are an Automation Generator Agent.
You are activated ONLY after:
- An automation plan has been created
- The user has explicitly approved the plan

You must strictly follow the approved plan.
You are NOT allowed to reinterpret, expand, or modify it.

Your task is to generate executable automation artifacts using ONLY free and open-source tools.

MANDATORY RULES:
1. Read and respect the approved automation plan exactly
   - Do NOT add new steps
   - Do NOT remove steps
   - Do NOT change tools
2. Generate only the artifacts needed for the plan
3. All generated code must be:
   - Runnable
   - Using only free/open-source libraries
   - Include basic logging and error handling
   - Follow best practices
4. Do NOT generate automation without user approval
5. Do NOT use paid APIs or proprietary tools
6. Do NOT hallucinate unavailable services

RETURN EXACTLY THIS STRUCTURE (valid JSON only):
{
  "generated_assets": {
    "python_scripts": [
      {
        "filename": "string",
        "description": "string",
        "content": "string (complete working code)"
      }
    ],
    "n8n_workflows": [
      {
        "filename": "string", 
        "description": "string",
        "content": "object (valid n8n JSON)"
      }
    ],
    "scheduler_instructions": [
      {
        "platform": "cron | windows | n8n",
        "instructions": "string"
      }
    ]
  },
  "run_instructions": ["string", "string"],
  "limitations": ["string", "string"]
}

No markdown. No explanations outside JSON. Return ONLY valid JSON."""
    
    def generate_automation(self, workflow, analysis_result, plan_result, approval_notes=""):
        """Generate executable automation assets from approved plan"""
        
        if not approval_notes and isinstance(approval_notes, str):
            approval_notes = ""
        
        system_prompt = self.get_generator_prompt()
        
        plan_context = json.dumps(plan_result, indent=2)
        analysis_context = json.dumps(analysis_result, indent=2)
        
        prompt = f"""APPROVED PLAN TO IMPLEMENT:
{plan_context}

ORIGINAL WORKFLOW ANALYSIS:
{analysis_context}

USER APPROVAL NOTES:
{approval_notes if approval_notes else 'None'}

Generate automation artifacts for this approved plan. Strictly follow the plan. Do not add, remove, or modify steps."""
        
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
            validated_output = self._validate_generation_response(raw_response)
            return {
                'success': True,
                'generated_assets': validated_output.get('generated_assets', {}),
                'run_instructions': validated_output.get('run_instructions', []),
                'limitations': validated_output.get('limitations', []),
                'metadata': {
                    'generated_at': self._get_timestamp(),
                    'plan_title': plan_result.get('plan_title'),
                    'approval_timestamp': self._get_timestamp()
                }
            }
        except ValueError as e:
            return {
                'success': False,
                'error': 'Generation failed',
                'message': str(e)
            }
    
    def _validate_generation_response(self, response_text):
        """Validate generation response structure"""
        try:
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if not json_match:
                raise ValueError("No JSON object found in response")
            
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            if 'generated_assets' not in data:
                raise ValueError("Missing 'generated_assets' field")
            
            assets = data['generated_assets']
            
            if 'python_scripts' not in assets:
                assets['python_scripts'] = []
            if 'n8n_workflows' not in assets:
                assets['n8n_workflows'] = []
            if 'scheduler_instructions' not in assets:
                assets['scheduler_instructions'] = []
            
            if not isinstance(assets['python_scripts'], list):
                raise ValueError("python_scripts must be a list")
            if not isinstance(assets['n8n_workflows'], list):
                raise ValueError("n8n_workflows must be a list")
            if not isinstance(assets['scheduler_instructions'], list):
                raise ValueError("scheduler_instructions must be a list")
            
            if 'run_instructions' not in data or not isinstance(data['run_instructions'], list):
                data['run_instructions'] = []
            
            if 'limitations' not in data or not isinstance(data['limitations'], list):
                data['limitations'] = []
            
            return data
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def export_python_script(self, assets, filename="automation_script.py"):
        """Export Python script to file"""
        script = assets.get('python_script', '')
        return {
            'filename': filename,
            'content': script,
            'size': len(script)
        }
    
    def export_n8n_workflow(self, assets, filename="automation_workflow.json"):
        """Export n8n workflow to file"""
        workflow = assets.get('n8n_workflow', {})
        return {
            'filename': filename,
            'content': json.dumps(workflow, indent=2),
            'size': len(json.dumps(workflow))
        }
    
    def export_scheduler_config(self, assets, filename="scheduler_config.txt"):
        """Export scheduler instructions to file"""
        instructions = assets.get('scheduler_instructions', {})
        content = self._format_scheduler_instructions(instructions)
        return {
            'filename': filename,
            'content': content,
            'size': len(content)
        }
    
    def _format_scheduler_instructions(self, instructions):
        """Format scheduler instructions into readable format"""
        output = []
        
        output.append("=== AUTOMATION SCHEDULER SETUP ===\n")
        
        if 'cron_format' in instructions:
            output.append("LINUX/macOS CRON:")
            output.append(f"  {instructions['cron_format']}\n")
        
        if 'windows_task' in instructions:
            output.append("WINDOWS TASK SCHEDULER:")
            output.append(f"  {instructions['windows_task']}\n")
        
        if 'notes' in instructions:
            output.append("NOTES:")
            output.append(f"  {instructions['notes']}\n")
        
        return '\n'.join(output)
