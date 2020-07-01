from flask import Flask, redirect, render_template, url_for, session, request
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "random"
app.config["static"] = "/Users/isayamin/desktop/BizTech/eSession3/static"

def authenticate(username, password=None):
    conn = sqlite3.connect('esession3.db')
    cursor = conn.cursor()
    if password == None: # for signup
        cursor.execute('SELECT username FROM Accounts WHERE username=?', (username, ))
    else: # for login
        cursor.execute('SELECT username FROM Accounts WHERE username=? AND password=?', (username, password))
    
    fetched_username = cursor.fetchone()
    print(fetched_username)
    conn.close()

    if fetched_username:
        return True
    else:
        return False

def createAccount(username, password):
    conn = sqlite3.connect('esession3.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO Accounts(username, password) VALUES(?,?)", (username, password))
    conn.commit()
    conn.close()

def getPosts(username):
    conn = sqlite3.connect('esession3.db')
    cursor = conn.cursor()

    cursor.execute('SELECT Title, Image, Description, Username FROM Posts WHERE username=?', (username, ))
    posts = cursor.fetchall()

    conn.close()

    return posts

def uploadPost(title, image, description, username):
    conn = sqlite3.connect('esession3.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO Posts(title, image, description, username) VALUES(?,?,?,?)', (title, image, description, username))

    conn.commit()
    conn.close()


@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        posts = getPosts(username)
        print(posts)
        return render_template('index.html', username=username, posts=posts)
    else:
        return render_template('login.html')

@app.route('/login', methods=["POST"])
def login():
    if request.form:
        username = request.form["username"]
        password = request.form["password"]
        if authenticate(username, password):
            session['username'] = username

    return redirect(url_for('index'))

@app.route('/logout', methods=["POST"])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/signup', methods=["POST"])
def signup():
    if request.form:
        username = request.form["username"]
        password = request.form["password"]
        if not authenticate(username): # if can create username
            createAccount(username, password)
            session["username"] = username
        else:
            print("Username already exists.")
    return redirect(url_for("index"))

@app.route('/uploadPost', methods=["POST"])
def upload():
    if request:
        title = request.form["title"]
        description = request.form["description"]
        username = session["username"]

        image = request.files["image"]
        filename = image.filename
        absolutePath = os.path.join(app.config["static"], filename)
        image.save(absolutePath)

        uploadPost(title, filename, description, username)
    return redirect(url_for('index'))


@app.route('/<catchall>')
def pagenotfound(catchall):
    return render_template('pagenotfound.html')

app.run(debug=True)