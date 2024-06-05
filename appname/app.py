import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask
from appname.views import danger_dtc

def create_app():
    app = Flask(__name__)

    # 注册 Blueprint
    app.register_blueprint(danger_dtc.bp)

    return app

if __name__ == "__main__":
    # create_app().run()
    create_app().run(debug=True)

