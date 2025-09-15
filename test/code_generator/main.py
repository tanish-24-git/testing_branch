import os
import json
import shutil
from core.planner import plan_project
from core.generator import generate_files
from core.debugger import debug_project
from core.runner import run_project
from operation.create_folder import create_folder
from operation.create_file import create_file

def code_generator(user_query):
    """
    Main function orchestrating the self-improving code generation process.
    Follows the specified flow: plan, scaffold, generate, run/test, debug loop, finalize.
    Uses modular components for scalability and maintainability.
    Handles backups during debugging for safety.
    Returns dict with files, test results, and instructions.
    """
    # Step 1: Planning
    plan = plan_project(user_query)

    # Step 2: Scaffolding
    root = plan["root_folder"]
    create_folder(root)

    # Create unique subfolders from file paths
    folders = set()
    for file_info in plan["files"]:
        dir_path = os.path.dirname(os.path.join(root, file_info["path"]))
        if dir_path and dir_path not in folders:
            create_folder(dir_path)
            folders.add(dir_path)

    # Create empty placeholder files
    for file_info in plan["files"]:
        create_file(os.path.join(root, file_info["path"]), "")

    # Collect dependencies and languages
    all_deps = set()
    languages = set()
    for file_info in plan["files"]:
        all_deps.update(file_info["dependencies"])
        languages.add(file_info["language"])

    # Auto-generate requirements.txt or package.json if deps exist
    if all_deps:
        py_deps = [d for d in all_deps if "python" in languages]  # Simplistic filter; assume format
        js_deps = [d for d in all_deps if "javascript" in languages]
        if py_deps:
            create_file(os.path.join(root, "requirements.txt"), "\n".join(py_deps))
        if js_deps:
            package_data = {
                "name": plan["project_name"],
                "version": "1.0.0",
                "dependencies": {}
            }
            for d in js_deps:
                if "==" in d:
                    name, version = d.split("==")
                elif "@" in d:
                    name, version = d.split("@")
                else:
                    name, version = d, "latest"
                package_data["dependencies"][name] = version
            create_file(os.path.join(root, "package.json"), json.dumps(package_data, indent=4))

    # Auto-generate README.md
    create_file(os.path.join(root, "README.md"), plan["guidance"])

    # Auto-generate .gitignore dynamically
    gitignore_content = """
__pycache__/
*.py[cod]
*.pyc
.env
"""
    if "javascript" in languages:
        gitignore_content += "node_modules/\n"
    create_file(os.path.join(root, ".gitignore"), gitignore_content)

    # Step 3: File Generation
    generated = generate_files(plan)
    for path, content in generated.items():
        create_file(os.path.join(root, path), content)

    # Step 4-5: Run/Test and Debugging Loop
    success, results = run_project(plan, root)
    retries = 0
    max_retries = 3  # Configurable; based on complexity if needed
    failing_files = generated.copy()  # Start with all; could narrow based on error
    while not success and retries < max_retries:
        edits_data = debug_project(results["error"], failing_files, plan)
        for edit in edits_data["edits"]:
            full_path = os.path.join(root, edit["path"])
            backup_path = full_path + ".bak"
            if os.path.exists(full_path):
                shutil.copy(full_path, backup_path)
            create_file(full_path, edit["new_content"])
            generated[edit["path"]] = edit["new_content"]
            failing_files[edit["path"]] = edit["new_content"]
        success, results = run_project(plan, root)
        retries += 1

    # Step 6: Finalization
    if not success:
        raise ValueError(f"Project generation failed after {max_retries} retries.")

    # Collect all files (generated + auto)
    files_list = [{"path": path, "content": content} for path, content in generated.items()]
    if os.path.exists(os.path.join(root, "requirements.txt")):
        with open(os.path.join(root, "requirements.txt"), "r") as f:
            files_list.append({"path": "requirements.txt", "content": f.read()})
    if os.path.exists(os.path.join(root, "package.json")):
        with open(os.path.join(root, "package.json"), "r") as f:
            files_list.append({"path": "package.json", "content": f.read()})
    files_list.append({"path": "README.md", "content": plan["guidance"]})
    files_list.append({"path": ".gitignore", "content": gitignore_content})

    return {
        "files": files_list,
        "test_results": results,
        "instructions": plan["guidance"]
    }

# Example usage
if __name__ == "__main__":
    user_query = "Create a simple Flask web app that says 'Hello World'."
    result = code_generator(user_query)
    print("Generated project instructions:")
    print(result["instructions"])