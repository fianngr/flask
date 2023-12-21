import os
from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_access_token
# from flask_mysqldb import MySQL
import sqlalchemy
import pymysql
import bcrypt

app = Flask(__name__)

# jwt = JWTManager(app)

# SECRET_KEY = os.environ.get('SECRET_KEY', 'rahasia')
# app.config['SECRET_KEY'] = SECRET_KEY

# MySQL configurations
# db_user = os.environ.get('CLOUD_SQL_USERNAME','root')
# db_password = os.environ.get('CLOUD_SQL_PASSWORD','root')
# db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME','foodwise')
# db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME','bangkit2023-402907:asia-southeast2:foodwise')

# mysql = MySQL(app)



# def open_connection():
#     unix_socket = '/cloudsql/{}'.format(db_connection_name)
#     conn = None  # Inisialisasi variabel conn di luar blok try
#     try:
#         if os.environ.get('GAE_ENV') == 'standard':
#             conn = pymysql.connect(
#                 user=db_user,
#                 password=db_password,
#                 unix_socket=unix_socket,
#                 db=db_name,
#                 cursorclass=pymysql.cursors.DictCursor
#             )
#     except pymysql.MySQLError as e:
#         return e
#     return conn


def connect_unix_socket() -> sqlalchemy.engine.base.Engine:
    """Initializes a Unix socket connection pool for a Cloud SQL instance of MySQL."""
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.
    db_user = os.environ["CLOUD_SQL_USERNAME"]  # e.g. 'my-database-user'
    db_pass = os.environ["CLOUD_SQL_PASSWORD"]  # e.g. 'my-database-password'
    db_name = os.environ["CLOUD_SQL_DATABASE_NAME"]  # e.g. 'my-database'
    unix_socket_path = os.environ[
        "INSTANCE_UNIX_SOCKET"
    ]  # e.g. '/cloudsql/project:region:instance'

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=<socket_path>/<cloud_sql_instance_name>
        sqlalchemy.engine.url.URL.create(
            drivername="mysql+pymysql",
            username=db_user,
            password=db_pass,
            database=db_name,
            query={"unix_socket": unix_socket_path},
        ),
        # ...
    )
    return pool



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
    
    try:
        conn = connect_unix_socket()
        print(conn)
        if conn is None:
            return jsonify({'error': 'Failed to establish a database connection'}), 500
        
        if not email or not username or not password:
            return jsonify({'error': 'Email, username, dan password diperlukan'}), 400

        with conn.connect() as connection:
            result = connection.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = result.fetchall()

            if user:
                return jsonify({'error': 'Username sudah terdaftar'}), 

            if user:
                return jsonify({'error': 'Username sudah terdaftar'}), 400

            # Hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Simpan user baru ke database
            sql = 'INSERT INTO users (email, username, password) VALUES (%s, %s, %s)'
            connection.execute(sql, (email, username, hashed_password))
           

            return jsonify({'message': 'Registrasi berhasil'}), 200

    except Exception as e:
        print(str(e))
        return jsonify({'error': 'Internal Server Error'}), 500
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login ():
    try:
        username = request.json['username']
        password = request.json['password']
        conn = connect_unix_socket()
        print(conn)
        if conn is None:
            return jsonify({'error': 'Failed to establish a database connection'}), 500

        with conn.connect() as connection:
            result = connection.execute("SELECT * FROM users WHERE username = %s", (username,))
            if result is None or result.rowcount == 0:
                return jsonify({'error': 'data kosong'}), 400
            user = result.fetchone()

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