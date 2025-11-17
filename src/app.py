import os
from src.DatabaseHelpers import downloadDatabase
from flask import Flask, render_template, request, jsonify
from src.DatabaseHandler import DatabaseHandler
import dotenv

app = Flask(__name__)

dotenv.load_dotenv()
db_path = os.path.join("..", "dataset", "finalDB.sqlite")
# Only download if missing
if not os.path.exists(db_path):
    print("Database file missing — downloading...")
    downloadDatabase(
        os.getenv("REPO_ID"),
        os.getenv("ACCESS_TOKEN"),
        os.getenv("DATABASE_FILENAME")
    )
else:
    print("Database file already present — skipping download.")
databaseHandler = DatabaseHandler("../dataset/finalDB.sqlite")
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
    start = data.get('start', '').strip()
    end = data.get('end', '').strip()

    if not start or not end:
        return jsonify(message="Both start and end article titles are required.", path=[], redirects=[])

    pathWithIds, redirects = databaseHandler.findShortestPath(start, end)

    if not pathWithIds:
        return jsonify(message="No path between the two articles was found.", path=[], redirects=redirects)

    pathWithNames = databaseHandler.convertIDsToNames(pathWithIds)

    # Build redirect messages
    redirect_msgs = []
    for src_id, target_id in redirects:
        src = databaseHandler.getNameFromID(src_id)
        target = databaseHandler.getNameFromID(target_id)
        redirect_msgs.append(f"‘{src}’ redirects to ‘{target}’.")  # typographic quotes for nicer look

    return jsonify(message=" ---> ".join(pathWithNames), path=pathWithNames, redirects=redirect_msgs)

if __name__ == '__main__':
    app.run(debug=True)

