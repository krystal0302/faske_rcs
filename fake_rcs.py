from flask import Flask
from flask import request, jsonify, g
import datetime
import sqlite3
import os

filename = os.path.abspath(os.path.dirname(__file__))
dbdir = os.path.abspath(os.path.join(filename.rstrip('filename.py'), os.path.pardir))
dbpath = os.path.join(dbdir, "farobot_dev_env/data/far_fleet_data/hik_data.db")

DATABASE = dbpath

class bcolors:
    black = '\033[30m'
    red = '\033[31m'
    green = '\033[32m'
    orange = '\033[33m'
    blue = '\033[34m'
    purple = '\033[35m'
    cyan = '\033[36m'
    lightgrey = '\033[37m'
    darkgrey = '\033[90m'
    lightred = '\033[91m'
    lightgreen = '\033[92m'
    yellow = '\033[93m'
    lightblue = '\033[94m'
    pink = '\033[95m'
    lightcyan = '\033[96m'
    ENDC = '\033[0m'

app = Flask(__name__)

stop_area = {
    "STK":{"indBind": 0},
    "TWIST":{"indBind": 0},
    "LIFTER":{"indBind": 0},
    "BUFFER":{"indBind": 0}
    }

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/resetAreaState")
def resetAreaState():
    global stop_area
    stop_area = {
    "STK":{"indBind": 0},
    "TWIST":{"indBind": 0},
    "LIFTER":{"indBind": 0},
    "BUFFER":{"indBind": 0}
    }
    return jsonify(stop_area)

@app.route("/getAreaState")
def getAreaState():
    global stop_area
    return jsonify(stop_area)

@app.route("/getHIKDataFromDB")
def getHIKDataFromDB():
    hik_data = ""
    
    hik_id = request.args.get('hik', default = "3328", type = str)
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    c_cursor = conn.cursor()
    
    c_cursor.execute("SELECT * from {}".format(f'hik{hik_id}'))
    for row in c_cursor.fetchall():
        hik_data = row
        
    print(hik_data)
    return jsonify(hik_data)

@app.route("/updateHIKDataToDB")
def updateHIKDataToDB():    
    hik_id = request.args.get('hik', default = "3328", type = str)
    hik_status = request.args.get('status', default = "2", type = str)
    posX = request.args.get('posX', default = "76134", type = str)
    posY = request.args.get('posY', default = "45652", type = str)

    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    c_cursor = conn.cursor()

    sql = f"UPDATE hik{hik_id} SET status=?, posX=?, posY=?" 
    
    c_cursor.execute(sql, (hik_status, posX, posY))
    conn.commit()

    return jsonify("ok")

@app.route("/cms/services/rest/hikRpcService/setAreaState", methods=['POST'])
def setAreaState():
    return_msg = {"message": ''}
    req = request.json
    area_name = req["matterArea"]
    indBind = int(req["indBind"])

    if area_name in stop_area:
        pass
    else:
        stop_area[area_name] = {"indBind": 0}
    
    if stop_area[area_name]["indBind"] == indBind:
        return_msg["message"] = "失敗"
        st = ""
        if indBind == 0:
            st = "release"
        else:
            st = "block"
        print(f"=== {area_name} alreay {st} !! ===")
    else:
        stop_area[area_name]["indBind"] = indBind
        return_msg["message"] = "成功"

    
    print(f"{bcolors.red}{getTime()}{bcolors.ENDC} --- {bcolors.yellow}{stop_area}{bcolors.ENDC}")
    # print(f"\033[33m{jsonify(return_msg)}\033[0m")
    return jsonify(return_msg)

@app.route("/cms/services/rest/hikRpcService/stopRobot", methods=['POST'])
def stopRobot():
    return_msg = {"message": '成功'}
    req = request.json
    robot_id = req["robots"]
    
    print(f"{bcolors.red}{getTime()}{bcolors.ENDC} --- Stop Agent: {bcolors.pink}{robot_id}{bcolors.ENDC}")
    # print(f"\033[33m{jsonify(return_msg)}\033[0m")
    return jsonify(return_msg)

@app.route("/cms/services/rest/hikRpcService/resumeRobot", methods=['POST'])
def resumeRobot():
    return_msg = {"message": '成功'}
    req = request.json
    robot_id = req["robots"]
    
    print(f"{bcolors.red}{getTime()}{bcolors.ENDC} --- Resume Agent: {bcolors.lightblue}{robot_id}{bcolors.ENDC}")
    # print(f"\033[33m{jsonify(return_msg)}\033[0m")
    return jsonify(return_msg)

@app.route("/cms/services/rest/hikRpcService/moveRobot", methods=['POST'])
def moveRobot():
    return_msg = {"message": '成功'}
    req = request.json
    robot_id = req["robotCode"]
    posX = req["endX"]
    posY = req["endY"]
    
    print(f"{bcolors.red}{getTime()}{bcolors.ENDC} --- Move Agent: {bcolors.cyan}{robot_id} {[posX, posY]}{bcolors.ENDC}")
    # print(f"\033[33m{jsonify(return_msg)}\033[0m")
    return jsonify(return_msg)

def getTime():
    now = datetime.datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv