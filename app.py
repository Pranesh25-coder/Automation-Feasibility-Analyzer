import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agents.analyzer import AutomationAnalyzer
from agents.planner import AutomationPlanner
from agents.generator import AutomationGenerator
from utils.validator import validate_workflow_input
from utils.y_combinator_demo import y_combinator_demo_payload

load_dotenv()

app = FastAPI(title="AI Automation Feasibility Analyzer")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = AutomationAnalyzer()
planner = AutomationPlanner()
generator = AutomationGenerator()


@app.post("/analyze")
def analyze(data: dict):
    try:
        if not data or "workflow" not in data:
            return JSONResponse({"error": "Missing 'workflow' field in request body"}, status_code=400)

        workflow = data.get("workflow")
        validate_workflow_input(workflow)

        result = analyzer.analyze(workflow)
        return JSONResponse(result, status_code=200)

    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)


@app.post("/plan")
def plan(data: dict):
    try:
        if not data or "workflow" not in data or "analysis" not in data:
            return JSONResponse({"error": "Missing 'workflow' or 'analysis' field in request body"}, status_code=400)

        workflow = data.get("workflow")
        analysis_result = data.get("analysis")

        if analysis_result.get("feasibility") == "NOT_AUTOMATABLE":
            return JSONResponse(
                {
                    "error": "Cannot create plan for non-automatable workflows",
                    "message": analysis_result.get("reason", "This workflow cannot be automated"),
                },
                status_code=400,
            )

        plan_result = planner.create_plan(workflow, analysis_result)

        if "error" in plan_result:
            return JSONResponse(plan_result, status_code=400)

        return JSONResponse(plan_result, status_code=200)

    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)


@app.post("/generate")
def generate(data: dict):
    try:
        required_fields = ["workflow", "analysis", "plan", "approval"]
        for field in required_fields:
            if field not in data:
                return JSONResponse({"error": f"Missing required field: {field}"}, status_code=400)

        if not data.get("approval"):
            return JSONResponse({"error": "Automation generation requires explicit user approval"}, status_code=400)

        workflow = data.get("workflow")
        analysis_result = data.get("analysis")
        plan_result = data.get("plan")
        approval_notes = data.get("approval_notes", "")

        result = generator.generate_automation(workflow, analysis_result, plan_result, approval_notes)

        if not result.get("success"):
            return JSONResponse(result, status_code=400)

        return JSONResponse(result, status_code=200)

    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)


@app.get("/health")
def health():
    return JSONResponse({"status": "ok"}, status_code=200)


@app.get("/demo/y-combinator")
def y_combinator_demo(n: int = Query(default=5)):
    if n < 0:
        return JSONResponse({"error": "Query parameter 'n' must be >= 0"}, status_code=400)
    return JSONResponse(y_combinator_demo_payload(n), status_code=200)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
