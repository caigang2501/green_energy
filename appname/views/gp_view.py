import sys,os
sys.path.append(os.getcwd())

from flask import request, jsonify,Blueprint,send_file
import main
import logging

bp = Blueprint("main", __name__)

@bp.route("/json", methods=['POST'])
def mid_long_year():
    hashrate = request.get_json()['hashrate']
    result = main.solve(hashrate)
    return jsonify(result)

@bp.route("/excel", methods=['POST'])
def mid_lon():
    hashrate = request.get_json()['hashrate']
    result = main.solve(hashrate)
    file_path = os.getcwd()+'/example/result/ans.xlsx'
    return send_file(file_path, as_attachment=True)

@bp.route("/get_excel", methods=['GET'])
def mid_get():
    file_path = os.getcwd()+'/example/result/ans.xlsx' 
    return send_file(file_path, as_attachment=True)
