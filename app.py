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