import os
from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

@app.route("/")
def hello_word():
    name = os.environ.get("NAME", "World")
    return "Hello{}!".format(name)



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