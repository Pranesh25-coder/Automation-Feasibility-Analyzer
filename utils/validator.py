import json
import re

REQUIRED_FIELDS = {
    "task_summary": str,
    "feasibility": str,
    "reason": str,
    "live_context_used": list,
    "assumptions": list,
    "constraints": list,
    "alternative_suggestions": list,
    "recommended_tools": list,
    "automation_plan": list,
    "manual_work_reduction": str,
    "validation_and_monitoring": list,
}

VALID_FEASIBILITY = {"FULLY_AUTOMATABLE", "PARTIALLY_AUTOMATABLE", "NOT_AUTOMATABLE"}


def validate_json_response(response_text):
    try:
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if not json_match:
            raise ValueError("No JSON object found in response")
        
        json_str = json_match.group(0)
        data = json.loads(json_str)
        
        for field, field_type in REQUIRED_FIELDS.items():
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(data[field], field_type):
                raise ValueError(f"Field '{field}' must be of type {field_type.__name__}")
        
        if data["feasibility"] not in VALID_FEASIBILITY:
            raise ValueError(f"Feasibility must be one of: {VALID_FEASIBILITY}")
        
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {str(e)}")


def validate_workflow_input(workflow):
    if not workflow or not isinstance(workflow, str):
        raise ValueError("Workflow must be a non-empty string")
    if len(workflow.strip()) < 10:
        raise ValueError("Workflow description must be at least 10 characters")
    return True
