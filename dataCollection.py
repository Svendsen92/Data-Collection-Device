#!/bin/python3
import sys
import socket
import platform
import calendar
import statistics

from datetime import datetime
from deviceLibrary.mySQL_DatabaseLib import mySQL_DatabaseLib # type: ignore
from deviceLibrary.myConstants import myConstants as const # type: ignore


if platform.system() == "Windows":
    password = const.password_windows # host PC's password
elif platform.system() == "Linux":
    password = const.password_linux # edgeDevice password
    import Adafruit_DHT # type: ignore
else:
    print("OS is not supported")
    exit()


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

def getInputArguments():
    ip: str = ""
    port: int = 12345
    try:
        # Get program argument for PORT number
        port = int(sys.argv[1])
    except:
        port = 12345
        print("Default PORT parameter has been used : " + str(port))
    finally:
        # Get local lan IP
        ip = get_myLocal_ip()
        print("IP = " + ip)
        print("PORT = " + str(port))

    return ip, port

def getSecondsSinceEpoch() -> int:
    n = datetime.now()
    t=datetime(n.year, n.month, n.day, n.hour, n.minute, n.second)
    return calendar.timegm(t.timetuple())

def DHT11_Sensor() -> dict:
    temperature = 0
    humidity = 0
    retDict = {"temp":temperature, "humidity":humidity, "GoodRead":False}

    DHT_Sensor = Adafruit_DHT.DHT11
    DHT_Pin = 4
    try:
        humidity, temperature = Adafruit_DHT.read(DHT_Sensor, DHT_Pin)
        retDict['temp'] = temperature
        retDict["humidity"] = humidity
        if (temperature != None and humidity != None):
            validTemperature = 0 <= temperature and temperature <= 60
            validHumidity = 20 <= humidity and humidity <= 90
            retDict['GoodRead'] = validTemperature and validHumidity
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
    except Exception as error:
        DHT11_Sensor.exit()
        raise error

    return retDict


##########################################
#### Data collection code starts here ####
def dataCollection() -> None:
    print("dataCollection()")

    # Create database object for dataCollection
    dataDB = mySQL_DatabaseLib(host=const.host, user=const.user, password=password, database=const.database)
    # Create database if it does not already exist
    dataDB.createDatabase(const.database)
    # Create table if it does not already exist
    ColumnNames = {"inputType": "VARCHAR(20)", "val": "FLOAT", "timeStamp": "DATETIME"}
    dataDB.createTable(tableName=const.dataTableName, columnHeaders=ColumnNames)

    humidityList: list = []
    temperatureList: list = []
    sensorUpdateTimer: int = getSecondsSinceEpoch()
    databaseUpdateTimer: int = getSecondsSinceEpoch()

    sensorReadInterval: int = 0 # 10secs
    sensorUpdateInterval: int = 0 # update interval in seconds (1800 = 30min)
    try:
        # Create database object for webInterface
        webDB = mySQL_DatabaseLib(host=const.host, user=const.user, password=password, database=const.database)
        sensorConfig = webDB.select(tableName=const.webTablename, header="sensorUpdateInterval, sensorReadInterval", condition="PK = 1")
        sensorUpdateInterval = sensorConfig[0]
        sensorReadInterval = sensorConfig[1]
    except:
        sensorReadInterval = 10 # 10secs
        sensorUpdateInterval = 1800 # update interval in seconds (1800 = 30min)

    print(f"sensorReadInterval: {sensorReadInterval}, sensorUpdateInterval: {sensorUpdateInterval}")

    while (True):

        if (getSecondsSinceEpoch() - sensorUpdateTimer >= sensorReadInterval): # update interval in seconds
            if platform.system() == "Linux":
                DHT_data = DHT11_Sensor()
            else:
                DHT_data = {"temp":0, "humidity":0, "GoodRead":False}
                DHT_data['GoodRead'] = True
                DHT_data['temp'] = 14.2
                DHT_data['humidity'] = 45.4

            if (DHT_data['GoodRead']):
                sensorUpdateTimer = getSecondsSinceEpoch()
                temperatureList.append(DHT_data["temp"])
                humidityList.append(DHT_data["humidity"])
                print("Temp=" + str(DHT_data['temp']) + "ºC, Humidity=" + str(DHT_data['humidity']))


        if (getSecondsSinceEpoch() - databaseUpdateTimer >= sensorUpdateInterval):
            databaseUpdateTimer = getSecondsSinceEpoch()

            try:
                # Update temperature in database
                timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                avgTemperature = statistics.median(temperatureList) 
                temperatureList.clear()  
                rowValues = ("Temperature", avgTemperature, timeStamp)
                dataDB.insert(tableName=const.dataTableName, headerStr="inputType, val, timeStamp", values=rowValues)
                print(f"Temp={avgTemperature}ºC, timeStamp={timeStamp}")
            except Exception as error:
                print(error)
                
            try:
                # Update humidity in database
                timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                avgHumidity =  statistics.median(humidityList)
                humidityList.clear()
                rowValues = ("Humidity", avgHumidity, timeStamp)
                dataDB.insert(tableName=const.dataTableName, headerStr="inputType, val, timeStamp", values=rowValues)
                print(f"Humidity={avgHumidity}, timeStamp={timeStamp}")
            except Exception as error:
                print(error)



#############################
#### Code starting point ####
if __name__ =="__main__":

    dataCollection()
    

