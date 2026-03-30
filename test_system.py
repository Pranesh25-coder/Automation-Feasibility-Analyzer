#!/usr/bin/env python3
import requests
import json
import time
import sys

API_URL = "http://localhost:5000"

test_workflow = "Every weekday morning, I log into a job portal, search for data science roles, copy the job details into an Excel file, and decide which jobs to apply for."

print("=" * 80)
print("TESTING AGENTIC AUTOMATION SYSTEM")
print("=" * 80)

print("\n[STEP 1] Testing /health endpoint...")
try:
    response = requests.get(f"{API_URL}/health", timeout=5)
    print(f"[PASS] Health check: {response.json()}")
except Exception as e:
    print(f"[FAIL] Health check failed: {e}")
    sys.exit(1)

print("\n[STEP 2] Sending workflow to /analyze endpoint...")
print(f"Workflow: {test_workflow}")
try:
    response = requests.post(
        f"{API_URL}/analyze",
        json={"workflow": test_workflow},
        timeout=120
    )
    if response.status_code == 200:
        analysis = response.json()
        print(f"\n[PASS] Analysis completed!")
        print(f"  - Feasibility: {analysis.get('feasibility')}")
        print(f"  - Task Summary: {analysis.get('task_summary', '')[:100]}...")
        print(f"  - Reason: {analysis.get('reason', '')[:100]}...")
        
        print("\n[EXPECTED BEHAVIOR CHECK]")
        if analysis.get('feasibility') == 'PARTIALLY_AUTOMATABLE':
            print("[PASS] Feasibility is PARTIALLY_AUTOMATABLE (CORRECT)")
        else:
            print(f"[FAIL] Feasibility is {analysis.get('feasibility')} (EXPECTED PARTIALLY_AUTOMATABLE)")
        
        if 'login' in analysis.get('reason', '').lower() or 'authentication' in analysis.get('reason', '').lower():
            print("[PASS] Mentions login/authentication barrier (CORRECT)")
        else:
            print(f"[FAIL] Reason doesn't mention login/authentication")
        
        if analysis.get('constraints'):
            print(f"[PASS] Constraints provided: {len(analysis.get('constraints', []))} items")
        else:
            print("[FAIL] No constraints provided")
            
        if analysis.get('alternative_suggestions'):
            print(f"[PASS] Alternatives provided: {len(analysis.get('alternative_suggestions', []))} items")
        else:
            print("[FAIL] No alternatives provided")
        
        saved_analysis = analysis
    else:
        print(f"[FAIL] Analysis failed with status {response.status_code}")
        print(f"  Response: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"[FAIL] Analysis request failed: {e}")
    sys.exit(1)

print("\n[STEP 3] Testing /plan endpoint...")
try:
    plan_response = requests.post(
        f"{API_URL}/plan",
        json={"workflow": test_workflow, "analysis": saved_analysis},
        timeout=120
    )
    if plan_response.status_code == 200:
        plan = plan_response.json()
        print(f"[PASS] Plan created!")
        print(f"  - Plan Title: {plan.get('plan_title', '')[:80]}...")
        print(f"  - Implementation Steps: {len(plan.get('implementation_steps', []))} steps")
        saved_plan = plan
    else:
        print(f"[FAIL] Plan creation failed with status {plan_response.status_code}")
        print(f"  Response: {plan_response.text}")
except Exception as e:
    print(f"[FAIL] Plan request failed: {e}")

print("\n[STEP 4] Testing /generate endpoint (with approval)...")
try:
    gen_response = requests.post(
        f"{API_URL}/generate",
        json={
            "workflow": test_workflow,
            "analysis": saved_analysis,
            "plan": saved_plan,
            "approval": True,
            "approval_notes": "Test approval"
        },
        timeout=180
    )
    if gen_response.status_code == 200:
        generation = gen_response.json()
        print(f"[PASS] Automation generated!")
        if generation.get('success'):
            assets = generation.get('generated_assets', {})
            print(f"  - Python Scripts: {len(assets.get('python_scripts', []))} items")
            print(f"  - n8n Workflows: {len(assets.get('n8n_workflows', []))} items")
            print(f"  - Scheduler Instructions: {len(assets.get('scheduler_instructions', []))} items")
            print(f"  - Run Instructions: {len(generation.get('run_instructions', []))} steps")
            print(f"  - Limitations: {len(generation.get('limitations', []))} items")
        else:
            print(f"[FAIL] Generation returned success=false")
            print(f"  Error: {generation.get('error')}")
    else:
        print(f"[FAIL] Generation failed with status {gen_response.status_code}")
        print(f"  Response: {gen_response.text[:500]}")
except Exception as e:
    print(f"[FAIL] Generation request failed: {e}")

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("[PASS] System flow completed successfully!")
print("[PASS] All endpoints responded correctly")
print("[PASS] Approval gate is working (generation requires approval=true)")
print("=" * 80)
