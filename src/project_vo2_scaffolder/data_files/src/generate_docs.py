#
# @project: Project VO2
# @file:    src/generate_docs.py
# @author:  Project VO2 Contributors
# @brief:   Generates project documentation from the project state file.
#
# This script reads the project's single source of truth (vo2_project_state.jsonl)
# and uses Jinja2 templates to generate a full set of Markdown documentation,
# including the main project charter and all Architecture Decision Records (ADRs).
#

import json
import os
from jinja2 import Environment, FileSystemLoader

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

STATE_FILE = os.getenv('STATE_FILE', os.path.join(PROJECT_ROOT, 'src/vo2_project_state.jsonl'))
TEMPLATE_DIR = os.getenv('TEMPLATE_DIR', os.path.join(PROJECT_ROOT, 'templates'))
OUTPUT_DIR = os.getenv('OUTPUT_DIR', os.path.join(PROJECT_ROOT, 'docs_generated'))


# --- Helper Functions ---
def load_project_state(file_path):
    """Loads the entire project state from the .jsonl file."""
    state = {
        'project_identity': {}, 'decisions': [], 'governance_model': {},
        'toolchain': {}, 'business_model': {}, 'repository_strategy': {}
    }
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                record_type = record.get('type')
                if record_type in state:
                    if isinstance(state[record_type], list):
                        state[record_type].append(record.get('data', {}))
                    else:
                        state[record_type] = record.get('data', {})
    except FileNotFoundError:
        print(f"ERROR: State file not found at '{file_path}'")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse JSON in {file_path}. Details: {e}")
        exit(1)

    state['decisions'] = sorted(state['decisions'], key=lambda x: x.get('decision_id', ''))
    return state

def render_template(env, template_name, context, output_path):
    """Renders a Jinja2 template and saves it to a file."""
    try:
        template = env.get_template(template_name)
        content = template.render(context)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully generated: {output_path}")
    except Exception as e:
        print(f"ERROR: Failed to render or write {output_path}: {e}")
        exit(1)


# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting Documentation Generator ---")
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False, trim_blocks=True, lstrip_blocks=True)
    project_state = load_project_state(STATE_FILE)

    print("\nGenerating main project documents...")
    render_template(env, 'README.md.j2', project_state, os.path.join(OUTPUT_DIR, 'README.md'))
    render_template(env, 'Project_Charter.md.j2', project_state, os.path.join(OUTPUT_DIR, 'Project_Charter.md'))

    print("\nGenerating Architecture Decision Records (ADRs)...")
    adr_output_dir = os.path.join(OUTPUT_DIR, 'decisions')
    for decision in project_state.get('decisions', []):
        decision_id = decision.get('decision_id')
        if decision_id:
            adr_path = os.path.join(adr_output_dir, f"{decision_id}.md")
            render_template(env, 'ADR.md.j2', {'decision': decision}, adr_path)

    print("\n--- Project generation complete! ---")

