from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login/login.html')

@app.route('/forgot')
def forgot():
    return render_template('login/forgot.html')

@app.route('/register')
def register():
    return render_template('login/register.html')

@app.route('/admin')
def admin():
    return render_template('admin/admon-bord.html')

@app.route('/search')
def search():
    return render_template('search/search.html')

if __name__ == '__main__':
    app.run(debug=True)