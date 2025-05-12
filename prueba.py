from flask import Flask, render_template, request, redirect, url_for, session
import pymysql
from pymysql.cursors import DictCursor
import requests

app = Flask(__name__)

app.secret_key = 'Charizard'

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
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM games")
            games = cursor.fetchall()

        return render_template('/admin/juegos.html', games=games, role=session.get('role'))
    except Exception as e:
        return f"Ocurrió un error: {e}"
    finally:
        connection.close()

@app.route('/carrito')
def carrito():
    if 'username' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    carrito = []
    total = 0

    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
                user = cursor.fetchone()
                if user:
                    cursor.execute("""
                        SELECT nombre, precio FROM cart_items
                        WHERE user_id = %s
                    """, (user['id'],))
                    carrito = cursor.fetchall()
                    total = sum(item['precio'] for item in carrito)
        finally:
            connection.close()

    return render_template('carrito.html', carrito=carrito, total=total, role=session.get('role'))

@app.route('/eliminar_item', methods=['POST'])
def eliminar_item():
    if 'username' not in session:
        return redirect(url_for('login'))

    nombre = request.form['nombre']
    connection = get_db_connection()

    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
                user = cursor.fetchone()
                if user:
                    cursor.execute("""
                        DELETE FROM cart_items
                        WHERE user_id = %s AND nombre = %s
                        LIMIT 1
                    """, (user['id'], nombre))
        finally:
            connection.close()
    return redirect('/carrito')

@app.route('/agregar_carrito', methods=['POST'])
def agregar_carrito():
    if 'username' not in session:
        return redirect(url_for('login'))

    nombre = request.form['nombre']
    precio = float(request.form['precio'])

    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
                user = cursor.fetchone()
                if user:
                    cursor.execute("SELECT stock FROM games WHERE name = %s", (nombre,))
                    game = cursor.fetchone()
                    if game:
                        cursor.execute("""
                            SELECT COUNT(*) AS cantidad_en_carrito
                            FROM cart_items
                            WHERE user_id = %s AND nombre = %s
                        """, (user['id'], nombre))
                        cantidad_en_carrito = cursor.fetchone()['cantidad_en_carrito']

                        if cantidad_en_carrito < game['stock']:
                            cursor.execute("""
                                INSERT INTO cart_items (user_id, nombre, precio)
                                VALUES (%s, %s, %s)
                            """, (user['id'], nombre, precio))
                        else:
                            return render_template('index.html', games=get_games(), role=session.get('role'), error=f"No hay más stock disponible para {nombre}.")
                    else:
                        return render_template('index.html', games=get_games(), role=session.get('role'), error=f"El juego {nombre} no existe.")
        finally:
            connection.close()

    return redirect('/index')

def get_games():
    """Helper function to fetch games from the database."""
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name, description, price, stock FROM games")
                return cursor.fetchall()
        finally:
            connection.close()
    return []

@app.route('/comprar', methods=['POST'])
def comprar():
    if 'username' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
                user = cursor.fetchone()

                if user:
                    user_id = user['id']
                    cursor.execute("""
                        SELECT nombre FROM cart_items
                        WHERE user_id = %s
                    """, (user_id,))
                    items = cursor.fetchall()

                    for item in items:
                        juego_nombre = item['nombre']
                        cursor.execute("""
                            UPDATE games
                            SET stock = stock - 1
                            WHERE name = %s AND stock > 0
                        """, (juego_nombre,))
                    cursor.execute("DELETE FROM cart_items WHERE user_id = %s", (user_id,))
        finally:
            connection.close()

    return render_template('compra_exitosa.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        numero = request.form['numero']
        connection = get_db_connection()
        if connection is None:
            return "No se pudo conectar a la base de datos. Intenta más tarde."

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    return "El usuario ya existe. Intenta con otro nombre de usuario."
                cursor.execute("INSERT INTO users (username, password, numero) VALUES (%s, %s, %s)", (username, password, numero))
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
                session['role'] = user.get('role', 'user')
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

            for game in games:
                query = f"{game['name']} game"
                api_url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2"
                print(f"Consultando Bing Image Search con URL: {api_url}")
                response = requests.get(api_url)
                if response.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    image_tags = soup.find_all('img', {'class': 'mimg'})
                    if image_tags:
                        # Usar la primera imagen relevante
                        game['image'] = image_tags[0]['src'] if 'src' in image_tags[0].attrs else 'https://via.placeholder.com/150'
                        print(f"Imagen obtenida para '{game['name']}': {game['image']}")
                    else:
                        game['image'] = 'https://via.placeholder.com/150'
                        print(f"No se encontraron imágenes para '{game['name']}'. Usando placeholder.")
                else:
                    game['image'] = 'https://via.placeholder.com/150'
                    print(f"Error al consultar Bing para '{game['name']}': {response.status_code}")
    except Exception as e:
        print(f"Error al procesar los juegos: {e}")
        return f"Ocurrió un error al obtener los juegos: {e}"
    finally:
        connection.close()
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
    app.run(host='0.0.0.0', port=5000, debug=True)
