from flask import Flask
from gs_mock import generate_mock_data

app = Flask(__name__)


base_url = "/api/v1"

app.add_url_rule(base_url + "/gs/mock", generate_mock_data)

if __name__ == "__main__":
    app.run(debug=True)
