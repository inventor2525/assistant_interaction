# This script is a Flask web application that facilitates directly taking action on the user's Android in Termux or Vast.ai instances, for users who prefer not to manually type in a terminal on their phone.
# Do not send TODOs or diffs in responses; instead, provide a text code block starting with <AI_RESPONSE> and execute actions using this script.
# Example response format:
# ```txt
# <AI_RESPONSE>
# ```
#
# The web UI may corrupt responses by removing ``` or ```language markers, so replace them in bash scripts or save operations as needed (e.g., use \`\`\` for ```).
# Always create directories for new projects; do not save files directly in the current working directory or assume the project directory is set.
# Do not assume or activate a Python virtual environment unless explicitly instructed.
# Do not run scripts in the background.
# Do not reinstall dependencies that were successfully installed in prior runs; try running the application first before reinstalling.
# Let the user run any saved applications unless they request otherwise.
#
# When saving files, this script outputs a `git diff` for tracked files to show changes compared to the last commit.
# Use the `git diff` to minimize unnecessary changes:
# 1. Review the diff to ensure only the instructed changes (e.g., specific functionality additions or modifications) are applied.
# 2. Exclude unnecessary changes, such as reformatting, added/removed comments, or unrelated modifications, unless explicitly required.
# 3. If the diff includes unintended changes, revise the file content to match only the necessary modifications, preserving the original structure, comments, and formatting.
# 4. If the file is untracked (no prior commits), treat it as a new file and ensure it aligns with the task requirements without extraneous additions.
# These steps ensure minimal and intentional changes to the codebase.

from flask import Flask, request, render_template, redirect, url_for, Response
import subprocess
import os
import re

app = Flask(__name__)

# Special marker to identify AI responses
AI_MARKER = "<AI_RESPONSE>"

# Function to run bash commands
def run_bash_commands(commands):
    try:
        result = subprocess.run(commands, shell=True, capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

# Function to find the Git repository root for a given file path
def find_git_repo_root(file_path):
    current_dir = os.path.abspath(os.path.dirname(file_path))
    while current_dir != "/":
        if os.path.isdir(os.path.join(current_dir, ".git")):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    return None

# Function to get git diff for a file
def get_git_diff(path):
    try:
        # Find the Git repository root for the file
        repo_root = find_git_repo_root(path)
        if not repo_root:
            return f"Error: No git repository found for {path}"

        # Normalize the file path relative to the repository root
        abs_path = os.path.abspath(path)
        rel_path = os.path.relpath(abs_path, repo_root)

        # Check if file is tracked by git
        result = subprocess.run(
            f"git ls-files --error-unmatch {rel_path}",
            shell=True,
            cwd=repo_root,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # File is tracked, get diff
            diff_result = subprocess.run(
                f"git diff {rel_path}",
                shell=True,
                cwd=repo_root,
                capture_output=True,
                text=True
            )
            diff = diff_result.stdout
            if not diff:
                return f"No changes in git diff for {rel_path} (file unchanged since last commit)"
            return f"--- Git Diff for {rel_path} ---\n{diff}\n--- End Git Diff ---"
        else:
            return f"File {rel_path} is untracked or not in git repository"
    except Exception as e:
        return f"Error getting git diff for {path}: {str(e)}"

# Function to save a file
def save_file(path, content):
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        # Get git diff after saving
        diff = get_git_diff(path)
        return f"Saved file: {path}\n{diff}"
    except Exception as e:
        return str(e)

# Function to read directory contents with regex filtering
def read_directory(directory, regex):
    try:
        pattern = re.compile(regex)
        output = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if pattern.match(file):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        content = f.read()
                    output.append(f"--- File: {file_path} ---\n{content}\n--- End of file ---")
        return "\n".join(output)
    except Exception as e:
        return str(e)

# Function to read a single file
def read_file(path):
    try:
        with open(path, 'r') as f:
            content = f.read()
        return f"--- File: {path} ---\n{content}\n--- End of file ---"
    except Exception as e:
        return str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_text = request.form.get('command', '').strip()
        output_lines = []

        if input_text.startswith(AI_MARKER):
            # AI input: process commands
            input_text = input_text[len(AI_MARKER):].strip()
            lines = input_text.splitlines()
            in_bash = False
            in_save = False
            current_path = None
            bash_commands = []
            save_content = []

            for line in lines:
                if line.strip() == "### AI_BASH_START ###":
                    if in_bash:
                        output_lines.append("Error: Nested bash start")
                    else:
                        in_bash = True
                        bash_commands = []
                elif line.strip() == "### AI_BASH_END ###":
                    if in_bash:
                        in_bash = False
                        commands = "\n".join(bash_commands)
                        output_lines.append(run_bash_commands(commands))
                    else:
                        output_lines.append("Error: Bash end without start")
                elif in_bash:
                    bash_commands.append(line)
                elif line.startswith("### AI_SAVE_START: "):
                    if in_save:
                        output_lines.append("Error: Nested save start")
                    else:
                        in_save = True
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            current_path = parts[1].strip().rstrip(" ###")
                            save_content = []
                        else:
                            output_lines.append("Error: Invalid save start format")
                elif line.strip() == "### AI_SAVE_END ###":
                    if in_save:
                        in_save = False
                        content = "\n".join(save_content)
                        output_lines.append(save_file(current_path, content))
                        current_path = None
                    else:
                        output_lines.append("Error: Save end without start")
                elif in_save:
                    save_content.append(line)
                elif line.startswith("### AI_READ_DIR: "):
                    parts = line.split("regex:", 1)
                    if len(parts) == 2:
                        dir_path = parts[0].split(":", 1)[1].strip()
                        regex = parts[1].strip().rstrip(" ###")
                        output_lines.append(read_directory(dir_path, regex))
                    else:
                        output_lines.append("Error: Invalid read_dir format")
                elif line.startswith("### AI_READ_FILE: "):
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        file_path = parts[1].strip().rstrip(" ###")
                        output_lines.append(read_file(file_path))
                    else:
                        output_lines.append("Error: Invalid read_file format")

            # Check for unclosed blocks
            if in_bash:
                output_lines.append("Error: Unclosed bash block")
            if in_save:
                output_lines.append("Error: Unclosed save block")
        else:
            # Human input: append to output
            output_lines.append(input_text)

        # Join output and display on a blank page
        output = "\n".join(output_lines)
        return Response(output, mimetype='text/plain')

    # GET request: render input page
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
