from flask import Flask
from .gs_mock import gs_mock

app = Flask(__name__)


base_url = "/api/v1"

app.add_url_rule(base_url + "/gs/mock", view_func=gs_mock, methods=["POST"])

if __name__ == "__main__":
    app.run(debug=True)
