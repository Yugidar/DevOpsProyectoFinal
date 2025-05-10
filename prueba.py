from flask import Flask, render_template, request, redirect, url_for
import pymysql
from pymysql.cursors import DictCursor

app = Flask(__name__)

# Database connection
def get_db_connection():
    try:
        connection = pymysql.connect(
            host='baseprueba24.ctu0c846233o.us-east-1.rds.amazonaws.com',
            user='admin24',
            password='prueba2424',
            database='usuarios',  # Updated database name
            charset='utf8mb4',
            cursorclass=DictCursor,
            autocommit=True  # Habilitar autocommit para evitar tener que hacer commit manual
        )
        return connection
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = get_db_connection()
        if connection is None:
            return "No se pudo conectar a la base de datos. Intenta más tarde."

        try:
            with connection.cursor() as cursor:
                # Check if the username already exists
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    return "El usuario ya existe. Intenta con otro nombre de usuario."
                # Insert the new user into the database
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            return redirect(url_for('login'))
        except Exception as e:
            return f"Ocurrió un error: {e}"
        finally:
            connection.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        if connection is None:
            return "No se pudo conectar a la base de datos. Intenta más tarde."

        try:
            with connection.cursor() as cursor:
                # Validate the user credentials
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                user = cursor.fetchone()
            if user:
                return redirect(url_for('index'))  # Redirect to the index page
            else:
                return "Credenciales incorrectas. Intenta de nuevo."
        except Exception as e:
            return f"Ocurrió un error: {e}"
        finally:
            connection.close()
    return render_template('login.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/')
def home():
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("La aplicación está abierta. Visita http://127.0.0.1:5000 en tu navegador.")
    app.run(debug=True)
