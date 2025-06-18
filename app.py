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
#
# Note that you can also read a block of code from 1 file straight into another by having 
# AI_READ_LINES in-between AI_SAVE_START and AI_SAVE_END. With it you can remove indentation or add it
# to match that of the file you are reading into.
# Eg:
#
# ```txt
# <AI_RESPONSE>
# ### AI_SAVE_START: /home/charlie/Projects/Alejandro_dev/assistant_interaction/assistant_interaction/core/utils.py ###
# import os
# import re
# import subprocess
# from pathlib import Path
# from typing import List, Optional
#
# from assistant_merger.git_tools import get_git_diff, add_change_numbers, apply_changes
#
# ### AI_READ_LINES: /home/charlie/Projects/Alejandro_dev/assistant_interaction/app.py:98:167 ###
#
# def process_command(input_text: str) -> str:
#     ### AI_READ_LINES: /home/charlie/Projects/Alejandro_dev/assistant_interaction/app.py:175:282:"-    " ###
#     return "\n".join(output_lines)
# ### AI_SAVE_END ###
# ### AI_READ_FILE: /home/charlie/Projects/Alejandro_dev/assistant_interaction/assistant_interaction/core/utils.py ###
# <END_OF_INPUT>
# ```
#
# Notice that it does not matter if AI_READ_LINES is indented, but that you can explicitly add indentation to read lines
# with "+        " or remove it with "- ". Notice you can remove or add any type of indent you need to in that way. Anything
# after the +/- will be added/removed from the beginning of each line that is read.
#
# Always be sure to pull your line numbers from the file you are trying to read lines from. Do not guess what they are!
#
# Calling AI_READ_FILE will give you the files contents, with line numbers. Do that, in a separate message, at least once,
# before you try to AI_READ_LINES from that file.

from flask import Flask, request, render_template, Response
from assistant_interaction.utils import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_text = request.form.get('command', '').strip()
        output = process_commands(input_text)
        return Response(output, mimetype='text/plain')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)