import os
import json
from flask import (
    Flask,
    request
)
app = Flask(__name__)

@app.route('/notifications/', methods=['GET'])
def get_notifications():
    # dummy code below
    max_notes = request.args.get('n', default=10, type=int)
    rev_sort = request.args.get('rev', default=0, type=int)
    rev_sort = False if rev_sort==0 else True
    level_filter = request.args.get('f', default=None, type=str)
    include_seen = request.args.get('seen', default=0, type=int)
    include_seen = False if include_seen==0 else True
    return json.dumps({
        "max_notes": max_notes,
        "rev_sort": rev_sort,
        "level_filter": level_filter,
        "include_seen": include_seen
    })
