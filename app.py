# This script is a Flask web application that facilitates directly taking action on the user's Android in Termux or Vast.ai instances, for users who prefer not to manually type in a terminal on their phone.
# Do not send TODOs or diffs in responses; instead, provide a text code block starting with <AI_RESPONSE> and execute actions using this script.
# Example response format:
# ```txt
# <AI_RESPONSE>
#...
# <END_OF_INPUT>
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
#
# Eg:
#
# ```txt
# <AI_RESPONSE>
# ### AI_SAVE_START: /data/data/com.termux/files/home/temp_projects/example_unit_alg_diff/vector2.py ###
# class Vector2:
#     """A 2D vector class for game development."""
#     def __init__(self, x: float, y: float):
#         self.x = x
#         self.y = y
# ### AI_SAVE_END ###
# ### AI_BASH_START ###
# # Create the temp_projects directory in the home directory
# mkdir -p /data/data/com.termux/files/home/temp_projects
# cd /data/data/com.termux/files/home/temp_projects

# # Clone the specified repositories
# git clone https://github.com/inventor2525/Alejandro.git
# git clone https://github.com/inventor2525/PrivateWebSpeech.git
# git clone https://github.com/inventor2525/RequiredAI.git
# git clone https://github.com/inventor2525/assistant_merger.git
# git clone https://github.com/inventor2525/assistant_interaction.git
# git clone https://github.com/inventor2525/graph_editor.git
# tree
# ### AI_BASH_END ###
# ### AI_READ_FILE: /data/data/com.termux/files/home/temp_projects/assistant_merger/assistant_merger/git_tools.py ###
# ### AI_READ_FILE: /data/data/com.termux/files/home/temp_projects/assistant_interaction/app.py ###
# <END_OF_INPUT>
# ```
# 
# Helpful tip, you may want to tree the projects dir when starting a new conversation, assume those repo's are there less
# stated otherwise.
#
# Also, if not run from a phone, the user may say they're in /home/charlie/Projects/Alejandro_dev if on the laptop or /workspace/ if on vast.ai (Assume we're on the phone though less you're told that, don't go checking for them there.)
#
# When saving you can then accept or deny your own changes.
# You should avoid making ANY un-nessisary or un-requested changes,
# but doing this by verbatim copying code is hard for LLMs so, this
# lets you undo un-nessisary changes that you made accidentally that
# would make a merge request harder. There is no need to simply say yes
# to all changes. You only need to respond if one of them, you wish to
# say no to.
#
# Eg:
# ```txt
# <AI_RESPONSE>
# ### AI_APPLY_CHOICES: /data/data/com.termux/files/home/temp_projects/example_unit_alg_diff/vector2.py ###
# Change #1, No
# Change #2, Yes
# ### AI_APPLY_CHOICES_END ###
# <END_OF_INPUT>
# ```
#
# You should get a diff for any changes you make to a file that exists
# in a git repo, but it may not be in one, in which case you can ignore
# this step.
#
# Do not presume what a diff is expected to be, and do not guess
# which changes you will accept or reject before receiving a diff
# from the application after you save a file.

from flask import Flask, request, render_template, redirect, url_for, Response
import subprocess
import os
import re
from pathlib import Path
from assistant_merger.git_tools import get_git_diff, add_change_numbers, apply_changes

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

# Function to save a file
def save_file(path, content):
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        # Get git diff using git_tools
        diff, error = get_git_diff(Path(path))
        if error:
            return f"Saved file: {path}\n{error}"
        # Generate hunk choices
        modified_diff, hunks = add_change_numbers(diff, Path(path), add_line_numbers=True)
        choices = [f"{hunk['number']}, (Yes/No)" for hunk in hunks]
        choices_output = f"### AI_CHOICES_START: {path} ###\n" + "\n".join(choices) + "\n### AI_CHOICES_END ###" if hunks else ""
        return f"Saved file: {path}\n{modified_diff}\n{choices_output}"
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
def read_file(path, add_line_numbers: bool = True):
    try:
        with open(path, 'r') as f:
            content = f.read()
        if add_line_numbers:
            lines = content.splitlines()
            numbered_lines = [f"{i+1:4d} {line}" for i, line in enumerate(lines)]
            content = "\n".join(numbered_lines)
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
            in_apply_choices = False
            current_path = None
            bash_commands = []
            save_content = []
            choices_content = []

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
                elif line.startswith("### AI_APPLY_CHOICES: "):
                    if in_apply_choices:
                        output_lines.append("Error: Nested apply choices start")
                    else:
                        in_apply_choices = True
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            current_path = parts[1].strip().rstrip(" ###")
                            choices_content = []
                        else:
                            output_lines.append("Error: Invalid apply choices format")
                elif line.strip() == "### AI_APPLY_CHOICES_END ###":
                    if in_apply_choices:
                        in_apply_choices = False
                        diff, error = get_git_diff(Path(current_path))
                        if error:
                            output_lines.append(f"Error: {error}")
                        else:
                            llm_response = "\n".join(choices_content)
                            merged_content = apply_changes(Path(current_path), diff, llm_response)
                            output_lines.append(save_file(current_path, merged_content))
                        current_path = None
                    else:
                        output_lines.append("Error: Apply choices end without start")
                elif in_apply_choices:
                    choices_content.append(line)
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
            if in_apply_choices:
                output_lines.append("Error: Unclosed apply choices block")
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