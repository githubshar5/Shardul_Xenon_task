python -m pip install --upgrade pip
from flask import Flask, render_template, request, session, redirect
from flask_mysqldb import MySQL,*
import hashlib

app = Flask(__name__)
app.secret_key = "secret-key"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'users_db'
mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", [username])
        user = cur.fetchone()
        if user and hashlib.sha256(password.encode()).hexdigest() == user[2]:
            session["loggedin"] = True
            session["id"] = user[0]
            session["username"] = user[1]
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid username or password")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    return redirect("/")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
        mysql.connection.commit()
        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "loggedin" in session:
        return render_template("dashboard.html", username=session["username"])
    else:
        return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
