#!/bin/python3
import sys
import socket
import platform
import calendar
import statistics
import logging

from datetime import datetime
from deviceLibrary.mySQL_DatabaseLib import mySQL_DatabaseLib # type: ignore
from deviceLibrary.myConstants import myConstants as const # type: ignore


if platform.system() == "Windows":
    password = const.password_windows # host PC's password
    from random import uniform
elif platform.system() == "Linux":
    password = const.password_linux # edgeDevice password
    import Adafruit_DHT # type: ignore
else:
    print("OS is not supported")
    exit()


# Create and configure logger
logging.basicConfig(filename="dataCollection_logFile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

# Creating an object
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.INFO)


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
        logger.info(f"get_myLocal_ip = {IP}")
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
def dataCollection(db: mySQL_DatabaseLib) -> None:
    print("dataCollection()")

    temperatureIdx: int = 0
    humidityIdx: int  = 1
    lightIdx: int = 2

    updateIntervalIdx: int = 0
    readIntervalIdx: int = 1

    configUpdateInterval: int = 11
    configUpdateTimer: int = getSecondsSinceEpoch()
    lightList: list[int] = []
    humidityList: list[int] = []
    temperatureList: list[int] = []
    sensorUpdateTimer: list[int] = [getSecondsSinceEpoch()] * len(const.sensorTypeList)
    databaseUpdateTimer: list[int] = [getSecondsSinceEpoch()] * len(const.sensorTypeList)
    is_sensorActivated: list[bool] = [False] * len(const.sensorTypeList)
    sensorConfig: list = []

    while (True):
        """ Check for updates to the sensor configuration """
        if (getSecondsSinceEpoch() - configUpdateTimer >= configUpdateInterval):
            configUpdateTimer = getSecondsSinceEpoch()
            is_sensorActivated.clear()
            sensorConfig.clear()
            for sensorType in const.sensorTypeList:
                """ Retrieve if the sensor is activated or not"""
                result = db.select(tableName=const.sensorTableName, header="is_active", condition=f"sensorType = '{sensorType}'")['result']
                is_sensorActivated.append(result[0][0])

                """ Retrieve the different read & update interval for each sensor, if None set to default value """
                result = db.select(tableName=const.sensorTableName, header="updateInterval, readInterval", condition=f"sensorType = '{sensorType}'")['result']
                sensorConfig.append(list(result[0]))
                # Check that database update interval has been set, else set it to default value
                if sensorConfig[len(sensorConfig) -1][0] == None:
                    sensorConfig[len(sensorConfig) -1][0] = 1800 # default value 15 minuts

                # Check that sensor read interval has been set, else set it to default value
                if sensorConfig[len(sensorConfig) -1][1] == None:
                    sensorConfig[len(sensorConfig) -1][1] = 10 # default vaule 10 secunds
                    


        """Temperature Sensor reading and Database updating"""
        if is_sensorActivated[temperatureIdx]:
            # Sensor read interval in seconds
            if (getSecondsSinceEpoch() - sensorUpdateTimer[temperatureIdx] >= sensorConfig[temperatureIdx][readIntervalIdx]):
                if platform.system() == "Linux":
                    DHT_data = DHT11_Sensor()
                else:
                    DHT_data = {"temp":0, "humidity":0, "GoodRead":False}
                    DHT_data['GoodRead'] = True
                    DHT_data['temp'] = uniform(-20, 80) # Outputs a random float between 1 and 10.

                if (DHT_data['GoodRead']):
                    sensorUpdateTimer[temperatureIdx] = getSecondsSinceEpoch()
                    temperatureList.append(DHT_data["temp"])

            # Sensor Database update interval in seconds
            if (getSecondsSinceEpoch() - databaseUpdateTimer[temperatureIdx] >= sensorConfig[temperatureIdx][updateIntervalIdx]):
                databaseUpdateTimer[temperatureIdx] = getSecondsSinceEpoch()
                try:
                    # Update temperature in database
                    timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    avgTemperature = statistics.median(temperatureList) 
                    temperatureList.clear()  
                    rowValues = ("Temperature", avgTemperature, timeStamp)
                    result = db.insert(tableName=const.dataTableName, header=["inputType", "value", "timeStamp"], values=rowValues)
                    logger.info(result['message'])
                    logger.info(f"Temp={avgTemperature}ºC, timeStamp={timeStamp}")
                except Exception as error:
                    logger.error(error)
                    

        """Humidity Sensor reading and Database updating"""
        if is_sensorActivated[humidityIdx]:
            # Sensor read interval in seconds
            if (getSecondsSinceEpoch() - sensorUpdateTimer[humidityIdx] >= sensorConfig[humidityIdx][readIntervalIdx]): 
                if platform.system() == "Linux":
                    DHT_data = DHT11_Sensor()
                else:
                    DHT_data = {"temp":0, "humidity":0, "GoodRead":False}
                    DHT_data['GoodRead'] = True
                    DHT_data['humidity'] = uniform(20, 100) # Outputs a random float between 1 and 10.

                if (DHT_data['GoodRead']):
                    sensorUpdateTimer[humidityIdx] = getSecondsSinceEpoch()
                    humidityList.append(DHT_data["humidity"])

            # Sensor Database update interval in seconds
            if (getSecondsSinceEpoch() - databaseUpdateTimer[humidityIdx] >= sensorConfig[humidityIdx][updateIntervalIdx]): 
                databaseUpdateTimer[humidityIdx] = getSecondsSinceEpoch()
                try:
                    # Update humidity in database
                    timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    avgHumidity =  statistics.median(humidityList)
                    humidityList.clear()
                    rowValues = ("Humidity", avgHumidity, timeStamp)
                    result = db.insert(tableName=const.dataTableName, header=["inputType", "value", "timeStamp"], values=rowValues)
                    logger.info(result['message'])
                    logger.info(f"Humidity={avgHumidity}, timeStamp={timeStamp}")
                except Exception as error:
                    logger.error(error)


        """Light Sensor reading and Database updating"""
        if is_sensorActivated[lightIdx]:
            # Sensor read interval in seconds
            if (getSecondsSinceEpoch() - sensorUpdateTimer[lightIdx] >= sensorConfig[lightIdx][readIntervalIdx]):             
                sensorUpdateTimer[lightIdx] = getSecondsSinceEpoch()
                lightList.append(999)

            # Sensor Database update interval in seconds
            if (getSecondsSinceEpoch() - databaseUpdateTimer[lightIdx] >= sensorConfig[lightIdx][updateIntervalIdx]): 
                databaseUpdateTimer[lightIdx] = getSecondsSinceEpoch()
                    
                try:
                    # Update Light in database
                    timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    avgLight =  statistics.median(lightList)
                    lightList.clear()
                    rowValues = ("Light", avgLight, timeStamp)
                    db.insert(tableName=const.dataTableName, header=["inputType", "value", "timeStamp"], values=rowValues)
                    logger.info(result['message'])
                    logger.info(f"Light={avgLight}, timeStamp={timeStamp}")
                except Exception as error:
                    logger.error(error)



#############################
#### Code starting point ####
if __name__ =="__main__":

    """ Create database object """
    db = mySQL_DatabaseLib(host=const.host, user=const.user, password=password, database=const.database)
    result = db.createDatabase(const.database) # Create database, if it does not already exist
    logger.info(f"INFO : {result['message']}")

    """ Create dataCollection_table, if it does not already exist """
    ColumnNames = {"inputType": "VARCHAR(20)", "value": "FLOAT", "timeStamp": "DATETIME"}
    result = db.createTable(tableName=const.dataTableName, columnHeaders=ColumnNames)
    logger.info(f"INFO : {result['message']}")

    """ Create webInterface_table, if it does not already exist """
    ColumnNames = {"deviceIP": "VARCHAR(15)", "deviceName": "VARCHAR(75)", "timeStamp": "DATETIME"}
    result = db.createTable(tableName=const.webTableName, columnHeaders=ColumnNames)
    logger.info(f"INFO : {result['message']}")
    if result['result']:
        header = ["deviceIP", "deviceName", "timeStamp"]
        timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        values: tuple = (get_myLocal_ip(), "RPi1", timeStamp)
        result = db.insert(tableName=const.webTableName, header=header, values=values)
        logger.info(f"INFO : {result['message']}")


    """ Create sensor_table, if it does not already exist """
    ColumnNames = {"sensorType": "VARCHAR(20)", "is_active": "BOOL", "updateInterval": "INT", "readInterval": "INT", "timeStamp": "DATETIME"}
    result = db.createTable(tableName=const.sensorTableName, columnHeaders=ColumnNames)
    logger.info(f"INFO : {result['message']}")
    if result['result']:
        header = ["sensorType", "is_active", "readInterval", "updateInterval", "timeStamp"]
        timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        values: tuple = (("temperature", False, 10, 1800, timeStamp), ("humidity", False, 10, 1800, timeStamp), ("light", False, 10, 1800, timeStamp))
        for valueSet in values:
            result = db.insert(tableName=const.sensorTableName, header=header, values=valueSet)
            logger.info(f"INFO : {result['message']}")



    # Data collection routine
    dataCollection(db=db)
    

