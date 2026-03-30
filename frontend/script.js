const API_URL = 'http://localhost:5000';

let currentWorkflow = '';
let currentAnalysis = null;
let currentPlan = null;

const form = document.getElementById('analysisForm');
const workflowInput = document.getElementById('workflowInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingContainer = document.getElementById('loadingContainer');
const resultContainer = document.getElementById('resultContainer');
const planContainer = document.getElementById('planContainer');
const generationContainer = document.getElementById('generationContainer');
const errorContainer = document.getElementById('errorContainer');
const errorMessage = document.getElementById('errorMessage');
const errorDismissBtn = document.getElementById('errorDismissBtn');
const resetBtn = document.getElementById('resetBtn');
const planBtn = document.getElementById('planBtn');
const approvePlanBtn = document.getElementById('approvePlanBtn');
const rejectPlanBtn = document.getElementById('rejectPlanBtn');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');
const downloadPythonBtn = document.getElementById('downloadPythonBtn');
const downloadWorkflowBtn = document.getElementById('downloadWorkflowBtn');
const downloadSchedulerBtn = document.getElementById('downloadSchedulerBtn');

form.addEventListener('submit', handleFormSubmit);
resetBtn.addEventListener('click', resetForm);
newAnalysisBtn.addEventListener('click', resetForm);
errorDismissBtn.addEventListener('click', dismissError);
planBtn.addEventListener('click', handlePlanRequest);
approvePlanBtn.addEventListener('click', handleApproval);
rejectPlanBtn.addEventListener('click', rejectPlan);
downloadPythonBtn.addEventListener('click', () => downloadAsset('python_script', 'automation_script.py'));
downloadWorkflowBtn.addEventListener('click', () => downloadAsset('n8n_workflow', 'automation_workflow.json'));
downloadSchedulerBtn.addEventListener('click', () => downloadAsset('scheduler_instructions', 'scheduler_config.json'));

async function handleFormSubmit(e) {
    e.preventDefault();

    const workflow = workflowInput.value.trim();

    if (!workflow) {
        showError('Please enter a workflow description.');
        return;
    }

    currentWorkflow = workflow;
    clearPreviousResults();
    showLoading('Analyzing your workflow...');

    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ workflow }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        currentAnalysis = data;
        displayResults(data);
    } catch (error) {
        showError(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

async function handlePlanRequest() {
    if (!currentWorkflow || !currentAnalysis) {
        showError('No analysis available. Please analyze a workflow first.');
        return;
    }

    if (currentAnalysis.feasibility === 'NOT_AUTOMATABLE') {
        showError('Cannot create a plan for non-automatable workflows.');
        return;
    }

    showLoading('Creating detailed automation plan...');
    clearPreviousResults();

    try {
        const response = await fetch(`${API_URL}/plan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                workflow: currentWorkflow,
                analysis: currentAnalysis
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        currentPlan = data;
        displayPlan(data);
    } catch (error) {
        showError(`Plan creation failed: ${error.message}`);
    } finally {
        hideLoading();
    }
}

async function handleApproval() {
    if (!currentPlan) {
        showError('No plan available for approval.');
        return;
    }

    const approvalNotes = document.getElementById('approvalNotes').value.trim();

    showLoading('Generating automation assets...');

    try {
        const response = await fetch(`${API_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                workflow: currentWorkflow,
                analysis: currentAnalysis,
                plan: currentPlan,
                approval: true,
                approval_notes: approvalNotes
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || errorData.message || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayGeneration(data);
    } catch (error) {
        showError(`Generation failed: ${error.message}`);
    } finally {
        hideLoading();
    }
}

function rejectPlan() {
    planContainer.classList.add('hidden');
    resultContainer.classList.remove('hidden');
    document.getElementById('approvalNotes').value = '';
}

function clearPreviousResults() {
    resultContainer.classList.add('hidden');
    planContainer.classList.add('hidden');
    generationContainer.classList.add('hidden');
    errorContainer.classList.add('hidden');
}

function showLoading(message = 'Processing...') {
    document.querySelector('.loading-container p').textContent = message;
    loadingContainer.classList.remove('hidden');
}

function hideLoading() {
    loadingContainer.classList.add('hidden');
}

function showError(message) {
    errorMessage.textContent = message;
    errorContainer.classList.remove('hidden');
}

function dismissError() {
    errorContainer.classList.add('hidden');
}

function displayResults(data) {
    document.getElementById('taskSummary').textContent = data.task_summary || '';
    document.getElementById('reason').textContent = data.reason || '';
    document.getElementById('manualReduction').textContent = data.manual_work_reduction || '';

    renderLiveContext(data.live_context_used || []);
    renderAssumptions(data.assumptions || []);
    renderConstraints(data.constraints || []);
    renderAlternatives(data.alternative_suggestions || []);
    renderTools(data.recommended_tools || []);
    renderAutomationPlan(data.automation_plan || []);
    renderValidation(data.validation_and_monitoring || []);
    renderFeasibility(data.feasibility || '');

    const planButton = document.getElementById('planBtn');
    if (data.feasibility !== 'NOT_AUTOMATABLE') {
        planButton.classList.remove('hidden');
    } else {
        planButton.classList.add('hidden');
    }

    resultContainer.classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function displayPlan(data) {
    document.getElementById('planTitle').textContent = data.plan_title || '';
    document.getElementById('planApproach').textContent = data.implementation_approach || '';
    document.getElementById('planDataFlow').textContent = data.data_flow || '';
    document.getElementById('planTrigger').textContent = data.trigger_mechanism || '';
    document.getElementById('monitoringStrategy').textContent = data.monitoring_strategy || '';
    document.getElementById('rollbackPlan').textContent = data.rollback_plan || '';

    renderToolSelection(data.tool_selection || []);
    renderImplementationSteps(data.implementation_steps || []);
    renderSuccessCriteria(data.success_criteria || []);
    renderTimeline(data.estimated_timeline || {});
    renderRiskMitigation(data.risk_mitigation || []);

    planContainer.classList.remove('hidden');
    resultContainer.classList.add('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function displayGeneration(data) {
    if (!data.success || !data.generated_assets) {
        showError('Generation failed: Invalid response structure');
        return;
    }

    const assets = data.generated_assets;
    const runInstructions = data.run_instructions || [];
    const limitations = data.limitations || [];

    renderGeneratedAssets(assets);
    renderRunInstructions(runInstructions);
    renderLimitations(limitations);

    window.generatedAssets = assets;

    generationContainer.classList.remove('hidden');
    planContainer.classList.add('hidden');
    resultContainer.classList.add('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function renderLiveContext(liveContext) {
    const list = document.getElementById('liveContextList');
    list.innerHTML = '';
    liveContext.forEach(context => {
        const li = document.createElement('li');
        li.textContent = context;
        list.appendChild(li);
    });
}

function renderAssumptions(assumptions) {
    const list = document.getElementById('assumptionsList');
    list.innerHTML = '';
    assumptions.forEach(assumption => {
        const li = document.createElement('li');
        li.textContent = assumption;
        list.appendChild(li);
    });
}

function renderConstraints(constraints) {
    const list = document.getElementById('constraintsList');
    list.innerHTML = '';
    constraints.forEach(constraint => {
        const li = document.createElement('li');
        li.textContent = constraint;
        list.appendChild(li);
    });
}

function renderAlternatives(alternatives) {
    const section = document.getElementById('alternativesSection');
    const list = document.getElementById('alternativesList');

    if (alternatives.length === 0) {
        section.classList.add('hidden');
        return;
    }

    section.classList.remove('hidden');
    list.innerHTML = '';
    alternatives.forEach(alt => {
        const li = document.createElement('li');
        li.textContent = alt;
        list.appendChild(li);
    });
}

function renderTools(tools) {
    const list = document.getElementById('toolsList');
    list.innerHTML = '';
    tools.forEach(tool => {
        const li = document.createElement('li');
        li.textContent = tool;
        list.appendChild(li);
    });
}

function renderAutomationPlan(plan) {
    const list = document.getElementById('planList');
    list.innerHTML = '';
    plan.forEach(step => {
        const li = document.createElement('li');
        li.textContent = step;
        list.appendChild(li);
    });
}

function renderValidation(validation) {
    const list = document.getElementById('validationList');
    list.innerHTML = '';
    validation.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        list.appendChild(li);
    });
}

function renderFeasibility(feasibility) {
    const badge = document.getElementById('feasibilityBadge');
    badge.innerHTML = '';

    const normalizedFeasibility = feasibility
        .toLowerCase()
        .replace(/_/g, '-');

    const displayText = feasibility
        .replace(/_/g, ' ')
        .replace(/\b\w/g, char => char.toUpperCase());

    badge.textContent = displayText;
    badge.className = `feasibility-badge ${normalizedFeasibility}`;
}

function renderToolSelection(tools) {
    const div = document.getElementById('toolSelectionDiv');
    div.innerHTML = '';
    tools.forEach(item => {
        const toolDiv = document.createElement('div');
        toolDiv.className = 'tool-item';
        toolDiv.innerHTML = `<strong>${item.tool || item}</strong>: ${item.justification || ''}`;
        div.appendChild(toolDiv);
    });
}

function renderImplementationSteps(steps) {
    const div = document.getElementById('implementationStepsDiv');
    div.innerHTML = '';
    const ol = document.createElement('ol');
    steps.forEach(step => {
        const li = document.createElement('li');
        if (typeof step === 'string') {
            li.textContent = step;
        } else {
            li.innerHTML = `<strong>${step.description || ''}</strong>` + 
                          (step.duration_estimate ? ` (${step.duration_estimate})` : '') +
                          (step.complexity ? ` - ${step.complexity}` : '');
        }
        ol.appendChild(li);
    });
    div.appendChild(ol);
}

function renderSuccessCriteria(criteria) {
    const list = document.getElementById('successCriteriaList');
    list.innerHTML = '';
    criteria.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        list.appendChild(li);
    });
}

function renderTimeline(timeline) {
    const div = document.getElementById('timelineDiv');
    div.innerHTML = '';
    const timelineItems = [
        { label: 'Setup', key: 'setup_days' },
        { label: 'Testing', key: 'testing_days' },
        { label: 'Deployment', key: 'deployment_days' },
        { label: 'Total', key: 'total_days' }
    ];
    timelineItems.forEach(item => {
        if (timeline[item.key]) {
            const p = document.createElement('p');
            p.innerHTML = `<strong>${item.label}:</strong> ${timeline[item.key]} days`;
            div.appendChild(p);
        }
    });
}

function renderRiskMitigation(risks) {
    const div = document.getElementById('riskMitigationDiv');
    div.innerHTML = '';
    risks.forEach(risk => {
        const riskDiv = document.createElement('div');
        riskDiv.className = 'risk-item';
        riskDiv.innerHTML = `
            <strong>${risk.risk || ''}</strong> (${risk.likelihood || 'medium'})
            <p>${risk.mitigation_strategy || ''}</p>
        `;
        div.appendChild(riskDiv);
    });
}

function renderGeneratedAssets(assets) {
    const configDiv = document.getElementById('configTemplateDiv');
    const depsList = document.getElementById('dependenciesList');
    const errorDiv = document.getElementById('errorHandling');
    const checklistDiv = document.getElementById('deploymentChecklist');

    configDiv.innerHTML = '';
    depsList.innerHTML = '';
    errorDiv.innerHTML = '';
    checklistDiv.innerHTML = '';

    if (assets.python_scripts && assets.python_scripts.length > 0) {
        const scriptSection = document.createElement('div');
        scriptSection.className = 'asset-group';
        assets.python_scripts.forEach((script, idx) => {
            const scriptDiv = document.createElement('div');
            scriptDiv.className = 'asset-item';
            scriptDiv.innerHTML = `
                <h4>${script.filename || 'Script ' + (idx + 1)}</h4>
                <p>${script.description || ''}</p>
                <button class="btn-secondary" onclick="downloadScript('${idx}')">Download</button>
            `;
            scriptSection.appendChild(scriptDiv);
        });
        configDiv.appendChild(scriptSection);
    }

    if (assets.n8n_workflows && assets.n8n_workflows.length > 0) {
        assets.n8n_workflows.forEach((workflow, idx) => {
            const li = document.createElement('li');
            li.textContent = `${workflow.filename || 'Workflow ' + (idx + 1)}: ${workflow.description || ''}`;
            depsList.appendChild(li);
        });
    }

    if (assets.scheduler_instructions && assets.scheduler_instructions.length > 0) {
        let schedulerText = '';
        assets.scheduler_instructions.forEach(instr => {
            schedulerText += `Platform: ${instr.platform}\n${instr.instructions}\n\n`;
        });
        errorDiv.textContent = schedulerText;
    }
}

function renderRunInstructions(instructions) {
    const checklistDiv = document.getElementById('deploymentChecklist');
    checklistDiv.innerHTML = '';
    instructions.forEach(instruction => {
        const li = document.createElement('li');
        li.textContent = instruction;
        checklistDiv.appendChild(li);
    });
}

function renderLimitations(limitations) {
    const listDiv = document.createElement('div');
    listDiv.className = 'limitations-list';
    limitations.forEach(limitation => {
        const item = document.createElement('li');
        item.textContent = limitation;
        listDiv.appendChild(item);
    });
    const section = document.querySelector('.download-section');
    if (section) {
        section.appendChild(listDiv);
    }
}

function downloadScript(scriptIdx) {
    if (!window.generatedAssets || !window.generatedAssets.python_scripts) {
        showError('No scripts available for download.');
        return;
    }

    const script = window.generatedAssets.python_scripts[scriptIdx];
    if (!script) {
        showError('Script not found.');
        return;
    }

    const blob = new Blob([script.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = script.filename || `script_${scriptIdx}.py`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function downloadAsset(assetType, filename) {
    if (!window.generatedAssets) {
        showError('No assets available for download.');
        return;
    }

    let content = '';
    let actualFilename = filename;

    if (assetType === 'python_script' && window.generatedAssets.python_scripts && window.generatedAssets.python_scripts[0]) {
        content = window.generatedAssets.python_scripts[0].content;
        actualFilename = window.generatedAssets.python_scripts[0].filename;
    } else if (assetType === 'n8n_workflow' && window.generatedAssets.n8n_workflows && window.generatedAssets.n8n_workflows[0]) {
        content = JSON.stringify(window.generatedAssets.n8n_workflows[0].content, null, 2);
        actualFilename = window.generatedAssets.n8n_workflows[0].filename;
    } else if (assetType === 'scheduler_instructions' && window.generatedAssets.scheduler_instructions && window.generatedAssets.scheduler_instructions[0]) {
        content = window.generatedAssets.scheduler_instructions[0].instructions;
    } else {
        showError(`No ${assetType} found in assets.`);
        return;
    }

    if (!content) {
        showError('Asset content is empty.');
        return;
    }

    const mimeType = assetType === 'n8n_workflow' ? 'application/json' : 'text/plain';
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = actualFilename || filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function resetForm() {
    currentWorkflow = '';
    currentAnalysis = null;
    currentPlan = null;
    workflowInput.value = '';
    workflowInput.focus();
    clearPreviousResults();
}
