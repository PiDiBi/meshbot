from flask import Flask, render_template_string
from db_operations import get_messages  # Assuming this function is in db_operations.py

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Messages</title>
</head>
<body>
    <h1>Messages</h1>
    <ul>
    {% for message in messages %}
        <li>
            <strong>[{{ message[3] }}]{{ message[1] }} ({{ message[2] }})</strong>: {{ message[5] }}
        </li>
    {% endfor %}
    </ul>
</body>
</html>
"""

@app.route('/')
def show_messages():
    messages = get_messages(100)
    return render_template_string(HTML_TEMPLATE, messages=messages)

@app.errorhandler(404)
@app.route('/404')
def page_not_found(e):
    return render_template_string('Page Not Found'), 404

@app.errorhandler(500)
@app.route('/500')
def error_page(e):
    return render_template_string(f'Error:<br /> {e}'), 404

def create_app():
   return app

if __name__ == '__main__':
    #app.run(debug=True)
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)

# run waitress-serve --port=8080 --call web:create_app to start the web server