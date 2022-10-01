from flask import Flask, request

from services import metrics_service
from services import repository_service

app = Flask(__name__)


@app.route("/repository")
def repository():
    return repository_service.get_repository(url=request.args['url'])


@app.route("/metrics", methods=["POST"])
def all_metrics():
    if request.headers.get('Content-Type') != 'application/json':
        return 'Content-Type not supported!', 415

    request_body = request.json
    repo_id, commits = request_body['repo_id'], tuple(request_body['commits'])
    languages = tuple(request_body.get('languages', metrics_service.ID_TO_LANGUAGE_NAME.keys()))
    get_currently_available = request_body.get('get_currently_available', True)

    return metrics_service.get_metrics(repo_id, commits, languages, get_currently_available)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
