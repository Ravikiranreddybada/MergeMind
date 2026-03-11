# TODO: Add Reasoning Section to AI Fix Generator

## Task: Upgrade AI "Reasoning" (Backend)
Modify backend/services/ai_fix_generator.py to have the AI explain its plan before writing code.

## Steps:

### Step 1: Update _analyze_issue_with_ai method
- [x] Modify the prompt to include a "Reasoning" section requirement
- [x] Add JSON mode to Groq API call for easy parsing
- [x] Update expected JSON response format to include:
  - `reasoning`: Step-by-step technical plan
  - `files_to_edit`: List of files to modify
  - `code_fix`: The actual code diff or full file content

### Step 2: Update _generate_ai_fix method
- [x] Include reasoning in the returned result
- [x] Ensure the reasoning is accessible in the final output

### Step 3: Add "Agent Thought Process" to UI (Frontend)
- [x] Added ReasoningBox component to frontend/app/runs/[id]/page.tsx
- [x] Updated RunDetail type to include reasoning fields
- [x] Added AI Analysis section with reasoning, files_to_edit, and code_fix display

### Step 4: Make the Logs look "Agentic" (Backend)
- [x] Updated "Analyzing repo" -> "Indexing repository structure and building context map..."
- [x] Updated "Generating fix" -> "Synthesizing code fix using Llama-3.1-70B reasoning engine..."
- [x] Updated "Creating PR" -> "Validating changes and finalizing GitHub Pull Request orchestration..."

