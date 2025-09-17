import json
import os
from jinja2 import Environment, FileSystemLoader

# --- Configuration ---
STATE_FILE = "vo2_project_state.jsonl"
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "docs_generated"


# --- Helper Functions ---
def load_project_state(file_path):
    """Loads the entire project state from the .jsonl file into a structured dictionary."""
    state = {
        "project_identity": {},
        "decisions": [],
        "governance_model": {},
        "toolchain": {},
        "business_model": {},
        "repository_strategy": {},
    }
    with open(file_path, "r") as f:
        for line in f:
            record = json.loads(line)
            if record["type"] == "project_identity":
                state["project_identity"] = record["data"]
            elif record["type"] == "decision_log":
                state["decisions"].append(record["data"])
            elif record["type"] in state:
                state[record["type"]] = record["data"]

    # Sort decisions for consistent output
    state["decisions"] = sorted(state["decisions"], key=lambda x: x["decision_id"])
    return state


def render_template(env, template_name, context, output_path):
    """Renders a Jinja2 template and saves it to a file."""
    template = env.get_template(template_name)
    content = template.render(context)
    with open(output_path, "w") as f:
        f.write(content)
    print(f"Successfully generated: {output_path}")


# --- Main Execution ---
if __name__ == "__main__":
    # 1. Setup Environment
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        os.makedirs(os.path.join(OUTPUT_DIR, "decisions"))

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    # 2. Load the single source of truth
    print(f"Loading project state from {STATE_FILE}...")
    project_state = load_project_state(STATE_FILE)

    # 3. Generate Main Project Files
    print("\nGenerating main project documents...")
    # Generate README.md
    render_template(
        env, "README.md.j2", project_state, os.path.join(OUTPUT_DIR, "README.md")
    )
    # Generate Project_Charter.md
    render_template(
        env,
        "Project_Charter.md.j2",
        project_state,
        os.path.join(OUTPUT_DIR, "Project_Charter.md"),
    )

    # 4. Generate Individual ADRs (Architecture Decision Records)
    print("\nGenerating Architecture Decision Records (ADRs)...")
    for decision in project_state["decisions"]:
        adr_filename = f"{decision['decision_id']}.md"
        adr_path = os.path.join(OUTPUT_DIR, "decisions", adr_filename)
        render_template(env, "ADR.md.j2", {"decision": decision}, adr_path)

    print("\n--- Project generation complete! ---")
    print(f"All files have been created in the '{OUTPUT_DIR}' directory.")
