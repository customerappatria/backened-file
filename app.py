from flask import Flask, jsonify
from flask_cors import CORS
from realtime_data import main
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/dashboard', methods=['GET'])
def dashboard_data():
    result = main()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT', 5000))
