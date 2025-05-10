from flask import Flask, render_template, request, redirect, url_for
from flask import session
import pymysql
from pymysql.cursors import DictCursor

app = Flask(__name__)

app.secret_key = 'una_clave_secreta'  # Añade esto si aún no lo tienes

def get_db_connection():
    try:
        connection = pymysql.connect(
            host='baseprueba24.ctu0c846233o.us-east-1.rds.amazonaws.com',
            user='admin24',
            password='prueba2424',
            database='usuarios',  
            charset='utf8mb4',
            cursorclass=DictCursor,
            autocommit=True  
        )
        return connection
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

@app.route('/admin/add', methods=['POST'])
def add_game():
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    stock = request.form['stock']

    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO games (name, description, price, stock)
                    VALUES (%s, %s, %s, %s)
                """, (name, description, price, stock))
        finally:
            connection.close()
    return redirect(url_for('admin'))

@app.route('/admin/update/<int:game_id>', methods=['POST'])
def update_game(game_id):
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    stock = request.form['stock']

    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE games SET name=%s, description=%s, price=%s, stock=%s
                    WHERE id=%s
                """, (name, description, price, stock, game_id))
        finally:
            connection.close()
    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:game_id>')
def delete_game(game_id):
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM games WHERE id = %s", (game_id,))
        finally:
            connection.close()
    return redirect(url_for('admin'))

@app.route('/admin')
def admin():
    connection = get_db_connection()
    if connection is None:
        return "No se pudo conectar a la base de datos. Intenta más tarde."
    
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    try:
        # Get games from the database
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM games")
            games = cursor.fetchall()
        return render_template('admin.html', games=games)
    except Exception as e:
        return f"Ocurrió un error: {e}"
    finally:
        connection.close()


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
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    return "El usuario ya existe. Intenta con otro nombre de usuario."
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
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                user = cursor.fetchone()
            if user:
                session['username'] = user['username']
                session['role'] = user.get('role', 'user')  # Si no tiene rol, asigna 'user'
                return redirect(url_for('index'))
            else:
                return "Credenciales incorrectas. Intenta de nuevo."
        except Exception as e:
            return f"Ocurrió un error: {e}"
        finally:
            connection.close()
    return render_template('login.html')

@app.route('/index')
def index():
    connection = get_db_connection()
    if connection is None:
        return "No se pudo conectar a la base de datos. Intenta más tarde."

    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name, description, price, stock FROM games")
            games = cursor.fetchall()
    except Exception as e:
        return f"Ocurrió un error al obtener los juegos: {e}"
    finally:
        connection.close()

    # Se pasa el rol almacenado en la sesión para usarlo en el template
    return render_template('index.html', games=games, role=session.get('role'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)

    return redirect(url_for('login'))

@app.route('/')
def home():
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("La aplicación está abierta. Visita http://127.0.0.1:5000 en tu navegador.")
    app.run(debug=True)
