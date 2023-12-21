import os
from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_access_token
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)

jwt = JWTManager(app)

SECRET_KEY = os.environ.get('SECRET_KEY', 'rahasia')
app.config['SECRET_KEY'] = SECRET_KEY

# MySQL configurations
app.config['MYSQL_HOST'] = '34.128.102.38'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'foodwise'
mysql = MySQL(app)



@app.route("/")
def hello_word():
    name = os.environ.get("NAME", "World")
    return "Hello{}!".format(name)

@app.route('/register',methods=['POST'])
def user_register():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    if not email or not username or not password:
            return jsonify({'error': 'Email, username, dan password diperlukan'}), 400
    try:
        db = mysql.connection.cursor()
        db.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Cek apakah username sudah terdaftar
        user = db.fetchone()

        if user:
            return jsonify({'error': 'Username sudah terdaftar'}), 400

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Simpan user baru ke database
        sql = 'INSERT INTO users (email, username, password) VALUES (%s, %s, %s)'
        db.execute(sql, (email, username, hashed_password))
        mysql.connection.commit()

        return jsonify({'message': 'Registrasi berhasil'}), 200

    except Exception as e:
        print(str(e))
        return jsonify({'error': 'Internal Server Error'}), 500
    finally:
        db.close()

@app.route('/login', methods=['POST'])
def login ():
    try:
        username = request.json['username']
        password = request.json['password']
        db = mysql.connection.cursor()
        db.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = db.fetchone()

        # Check if the user exists
        if user:
            hashed_password = user[3] 
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                # print(user[3])
                    # Jika password valid, buat token JWT
                token = create_access_token(identity={'username': user[2]})
                return jsonify({
                    'message': 'Login Success',
                    'token_jwt': token
                }), 200
            else:
                return jsonify({'error': 'Username atau password salah'}), 401
    except Exception as e:
        print(str(e))
        return jsonify({'error': 'Internal Server Error'}), 500

SWAGGER_URL = '/swagger'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.json'  # Our API url (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "foodwise application"
    },
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0",port=int(os.environ.get("PORT",8080)))