from flask import Flask, jsonify
from flask_cors import CORS
from realtime_data import main  

app = Flask(__name__)
CORS(app)  

@app.route('/api/dashboard', methods=['GET'])
def dashboard_data():
    result = main()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
