# Environment Monitoring System

### *Objective*
The objective of the repository is twofold: 1) To create a small formfactor data collection device, that gathers data about the environment (temperature, humidity, light intensity, Co2, etc). The device has to be easily configurable and able to run a database, in which all device related and sensor data is stored. 2) To create a website application from which multiple devices can be add and their data viewed. There must be features such as login for different users, graphing of the data delivered by the associated data collection devices. 


### *Hardware*
The small formfactor data collection device used is a Raspberry Pi3.
  - Temperature & Humidity Sensor --> DHT11
  - Light Intensity Sensor --> Photosensitive Resistance LDR


### *How to get it running*
The Libraries required to be installed on the Raspberry Pi:
1. sudo apt update & sudo apt upgrade --> (Always do this)
2. sudo pip install Adafruit-DHT --> (Used for interacting with the temperature & humidity sensor)
3. sudo pip install mysql-connector-python --> (Used for interaction with mySQL database)
4. Used to install mariaDB on linux --> [tutorial link](https://raspberrytips.com/install-mariadb-raspberry-pi/)


The Libraries required to be installed on the computer:
1. TBD
2. TBD

<br>
Now the libraries & programs needed should be ready.

### *How to use to application*
In progress


### *To be done*

- Webapplication:
  * Make page for adding/removing data collection devices.
      - Make function to search for data collection devices to be added
      - Make function to add/remove read and write privileges to the webapplication from the collection device. 
  * Make page that displays graphs of the data from a data collection device.

- Raspberry Pi:
  * Make a function to connect to a wifi network using SSID & Password.
  * Make webinterface prettier.


### *License* 

