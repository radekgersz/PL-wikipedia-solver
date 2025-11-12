from pyexpat.errors import messages

from flask import Flask, render_template, request, jsonify
from DatabaseHandler import DatabaseHandler
import dotenv

app = Flask(__name__)

dotenv.load_dotenv()
# datasetPath = downloadDatabase(os.getenv("REPO_ID"), os.getenv("ACCESS_TOKEN"),os.getenv("DATABASE_FILENAME"))
databaseHandler = DatabaseHandler("/home/radek-gersz/PycharmProjects/PL-wikipedia-solver/dataset/finalDB.sqlite")
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    suggestions = databaseHandler.getTitlesStartingWith(query)
    return jsonify(suggestions)
@app.route('/find', methods=['POST'])
def find():
    data = request.get_json()
    start = data.get('start','null')
    end = data.get('end','null')
    pathWithIds = databaseHandler.findShortestPath(start,end)
    if not pathWithIds:
        return jsonify(message="No path between the two articles was found!")
    pathWithNames = databaseHandler.convertIDsToNames(pathWithIds)
    return jsonify(message="Path found.", path=pathWithNames)
if __name__ == '__main__':
    app.run(debug=True)

