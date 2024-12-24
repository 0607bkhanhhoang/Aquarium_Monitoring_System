from flask import Flask, request

app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return "Welcome to the Simple Flask Web App!"

# About page
@app.route('/about')
def about():
    return "This is the about page."

# Dynamic route with a parameter
@app.route('/greet/<name>')
def greet(name):
    return f"Hello, {name}! Welcome to the web app."

# Route with query parameters
@app.route('/search')
def search():
    # Access query parameters (e.g., /search?query=Flask)
    query = request.args.get('query', 'Nothing')
    return f"You searched for: {query}"

# Handling both GET and POST requests
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        # Handle form data (assuming a form sends 'username')
        username = request.form.get('username', 'Guest')
        return f"Form submitted successfully! Hello, {username}!"
    else:
        return "Submit a form with a POST request to this route."

if __name__ == '__main__':
    app.run(debug=True)
