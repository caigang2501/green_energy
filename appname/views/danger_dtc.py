import sys,os
sys.path.append(os.getcwd())

from flask import request, jsonify,Blueprint
import main
import logging

bp = Blueprint("main", __name__)

@bp.route("/mstEdges", methods=['POST'])
def mid_long_year():
    data = request.get_json()['points']
    result = main.mst_edge(data)
    return jsonify(result)
