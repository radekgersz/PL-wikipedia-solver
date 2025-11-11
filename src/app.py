from flask import Flask, render_template, request, jsonify
from DatabaseHelpers import downloadDatabase, createSQLiteEngine
import os
import dotenv

app = Flask(__name__)

dotenv.load_dotenv()
datasetPath = downloadDatabase(os.getenv("REPO_ID"), os.getenv("ACCESS_TOKEN"),os.getenv("DATABASE_FILENAME"))
engine = createSQLiteEngine(datasetPath)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/hello', methods=['POST'])
def hello():
    data = request.get_json()
    name = data.get('name', 'stranger')
    return jsonify(message=f"Hello, {name}!")

@app.route('/find', methods=['POST'])
def find():
    data = request.get_json()
    start = data.get('start','chuj')
    end = data.get('end','chuj')
    return jsonify(message=f"Hello, {start}-{end}!")
if __name__ == '__main__':
    app.run(debug=True)

