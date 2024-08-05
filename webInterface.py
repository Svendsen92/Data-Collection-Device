#!/bin/python3
import socket
import platform

from datetime import datetime
from deviceLibrary.mySQL_DatabaseLib import mySQL_DatabaseLib # type: ignore
from deviceLibrary.myConstants import myConstants as const # type: ignore
from flask import Flask, render_template, redirect, url_for, request # type: ignore


# Determine the operating system of this device
if platform.system() == "Windows":
    password_sqlDB = const.password_windows # host PC's password
elif platform.system() == "Linux":
    password_sqlDB = const.password_linux # edgeDevice password
    import subprocess
else:
    print("OS is not supported")
    exit()


# Create database object
db = mySQL_DatabaseLib(host=const.host, user=const.user, password=password_sqlDB, database=const.database)


######################################
#### Common functions starts here ####
def get_myLocal_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't have to be reachable
        s.connect(('192.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def findAvailableWifi() -> list[str]:
    print("findAvailableWifi()")
     # using the check_output() for having the network term retrieval
    devices = subprocess.check_output("sudo iw dev wlan0 scan | grep SSID", shell=True)

    # decode it to strings
    devices = devices.decode('ascii')
    devices= devices.replace("\r","")
    devices= devices.replace("\n","")
    devices= devices.replace("\t","")

    devices= devices.split("SSID: ")
    devices = list(dict.fromkeys(devices)) #Remove duplicates
    for device in devices:
            if device == "" or device.find("SSID") > 0:
                    devices.remove(device)

    print(f"devices : {devices}")
    return devices

def connectToWifi(ssid: str, password: str) -> bool:
    print("connectToWifi()")
    print(f"ssid = {ssid}, password = {password}")

    # Connect to wifi
    try:
        conn = subprocess.check_output(f"sudo iwconfig wlan0 essid {ssid} key {password}", shell=True)
        conn = conn.decode("utf-8")
        print(f"conn : {conn}")
        return True
    except Exception as error:
        print(error)
        return False
    

##########################################
#### Web Application code starts here ####
app = Flask(__name__)

@app.route("/")
def defaultPage():
    print("/")
    return redirect(url_for('homePage'))


@app.route("/homePage", methods=['POST', 'GET'])
def homePage():

    # list that contains the different sensor types
    sensorTypeList : list = const.sensorTypeList

    if 'homePage_Next_Btn' in request.form:
        deviceName = request.form['deviceName_Input']
        if not db.update(tableName=const.webTablename, header=["deviceName"], values=(deviceName), condition="PK = 1"):
            db.insert(tableName=const.webTablename, header=["deviceName"], values=(deviceName))

        # Update sensor setting or insert them if not already created 
        #for i in range(0, len(sensorTypeList)):
        for sensorType in sensorTypeList: 
            # Detect if the checkbox for each sensor is checked
            is_checked = False
            try:
                is_checked = bool(request.form[sensorType + '_chkBox'])
            except Exception as error:
                pass
            # Update the sensor table with the 'is_active' according to the checkbox result, or insert it if not already created
            if not db.update(tableName=const.sensorTableName, header=["is_active"], values=(is_checked), condition=f"sensorType = '{sensorType}'"):
                db.insert(tableName=const.sensorTableName, header=["is_active"], values=(is_checked))

            # Update the sensor table with the 'readInterval' according to the 'specified Sensor'_readInterval_input result, or insert it if not already created
            readInterval = request.form[sensorType + '_readInterval_input']
            if not db.update(tableName=const.sensorTableName, header=["readInterval"], values=(readInterval), condition=f"sensorType = '{sensorType}'"):
                db.insert(tableName=const.sensorTableName, header=["readInterval"], values=(readInterval))
            
            # Update the sensor table with the 'updateInterval' according to the 'specified Sensor'_updateDbInterval_input result, or insert it if not already created
            updateInterval = request.form[sensorType + '_updateDbInterval_input']
            if not db.update(tableName=const.sensorTableName, header=["updateInterval"], values=(updateInterval), condition=f"sensorType = '{sensorType}'"):
                db.insert(tableName=const.sensorTableName, header=["updateInterval"], values=(updateInterval))

        return redirect(url_for('wifiSetupPage'))
    else:
        # Retrive the existing data for each sensor and pass it to the front-end be rendered
        isCheckedList: list = []
        readInterval: list = []
        updateInterval: list = []

        #for i in range(0, len(sensorTypeList)):
        for sensorType in sensorTypeList:
            isCheckedList.append(db.select(tableName=const.sensorTableName,  header="is_active", condition=f"sensorType = '{sensorType}'"))
            if isCheckedList[len(isCheckedList) -1] != None:
                isCheckedList[len(isCheckedList) -1] = db.select(tableName=const.sensorTableName,  header="is_active", condition=f"sensorType = '{sensorType}'")[0][0]
            
            readInterval.append(db.select(tableName=const.sensorTableName,  header="readInterval", condition=f"sensorType = '{sensorType}'"))
            if readInterval[len(readInterval) -1] != None:
                readInterval[len(readInterval) -1] = db.select(tableName=const.sensorTableName,  header="readInterval", condition=f"sensorType = '{sensorType}'")[0][0]

            updateInterval.append(db.select(tableName=const.sensorTableName,  header="updateInterval", condition=f"sensorType = '{sensorType}'"))
            if updateInterval[len(updateInterval) -1] != None:
                updateInterval[len(updateInterval) -1] = db.select(tableName=const.sensorTableName,  header="updateInterval", condition=f"sensorType = '{sensorType}'")[0][0]

        return render_template('homePage.html', isCheckedList=isCheckedList, readInterval=readInterval, updateInterval=updateInterval)
    


@app.route('/wifiSetupPage', methods=['POST'])
def wifiSetupPage():
    print("wifiSetupPage")

    if platform.system() == "Windows":
        ssids_list = ["SSID: one", "SSID: two", "SSID: three"]
    elif platform.system() == "Linux":
        ssids_list = findAvailableWifi()
    else:
        print("OS is not supported")
        exit()
    
    if 'connectRequest' in request.form:
        ssid = request.form['dropdown_SSID']
        password = request.form['password']
        is_connected = connectToWifi(ssid=ssid, password=password)
        print(f"is_connected: {is_connected}")

        if is_connected:
            ##return render_template('sensorSetupPage.html')
            print("Success")
        else:
            print("failure")
    else:
        return render_template('wifiSetupPage.html', ssids_list=ssids_list)




#############################
#### Code starting point ####
if __name__ =="__main__":

    # Create database if it does not already exist
    db.createDatabase(const.database)

    # Create webInterface_table, if it does not already exist
    ColumnNames = {"deviceIP": "VARCHAR(15)", "deviceName": "VARCHAR(75)", "timeStamp": "DATETIME"}
    if db.createTable(tableName=const.webTablename, columnHeaders=ColumnNames):
        header = ["deviceIP", "deviceName", "timeStamp"]
        timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        values: tuple = (get_myLocal_ip(), "RPi1", timeStamp)
        status = db.insert(tableName=const.webTablename, header=header, values=values)
        print(f"Insert status: {status}")


    # Create sensor_table, if it does not already exist
    ColumnNames = {"sensorType": "VARCHAR(20)", "is_active": "BOOL", "updateInterval": "INT", "readInterval": "INT", "timeStamp": "DATETIME"}
    if db.createTable(tableName=const.sensorTableName, columnHeaders=ColumnNames):
        header = ["sensorType", "is_active", "readInterval", "updateInterval", "timeStamp"]
        timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        values: tuple = (("temperature", False, 10, 1800, timeStamp), ("humidity", False, 10, 1800, timeStamp), ("light", False, 10, 1800, timeStamp))
        for valueSet in values:
            print(valueSet)
            status = db.insert(tableName=const.sensorTableName, header=header, values=valueSet)
            print(f"Insert status: {status}")


    app.run("127.0.0.1", 5500)
    