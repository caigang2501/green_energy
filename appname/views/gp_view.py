import sys,os
sys.path.append(os.getcwd())

from flask import request, jsonify,Blueprint,send_file
import main
import logging

bp = Blueprint("main", __name__)

@bp.route("/json", methods=['POST'])
def json():
    load = request.get_json()['load']
    result = main.solve(load)
    return jsonify(result)

@bp.route("/excel", methods=['POST'])
def excel():
    load = request.get_json()['load']
    main.solve(load)
    file_path = os.getcwd()+'/example/result/ans.xlsx'
    return send_file(file_path, as_attachment=True)

@bp.route("/get_excel", methods=['GET'])
def get_excel():
    file_path = os.getcwd()+'/example/result/ans.xlsx' 
    return send_file(file_path, as_attachment=True)
