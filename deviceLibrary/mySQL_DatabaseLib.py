import mysql.connector # type: ignore


class mySQL_DatabaseLib:
    def __init__(self, host: str, user: str, password: str, database: str):
        self._host = host
        self._user = user
        self._password = password
        self._database = database


    def createDatabase(self, databaseName: str) -> dict:
        mydb = mysql.connector.connect(
            host=self._host,
            user=self._user,
            password=self._password
        )

        try:
            mycursor = mydb.cursor()
            mycursor.execute(f"CREATE DATABASE {databaseName}")
            return {'result':True,'message':f"Database<{databaseName}> has been created"}
        except Exception as error:
            return {'result':False,'message':error}


    def createTable(self, tableName: str, columnHeaders: dict) -> dict:
        mydb = mysql.connector.connect(
            host=self._host,
            user=self._user,
            password=self._password,
            database=self._database
        )

        sql_headerString = ""
        for header in columnHeaders:
            sql_headerString += header
            sql_headerString += " "
            sql_headerString += columnHeaders[header]
            sql_headerString += ", "

        res = sql_headerString[: len(sql_headerString)-2]  
        mycursor = mydb.cursor()
        try:
            mycursor.execute(f"CREATE TABLE {tableName} (PK INT AUTO_INCREMENT NOT NULL, {res}, PRIMARY KEY (PK))")
            return {'result':True,'message':f"Table<{tableName}> has been created"}
        except Exception as error:
            return {'result':False,'message':error}


    def showDatabases(self):
        mydb = mysql.connector.connect(
            host=self._host,
            user=self._user,
            password=self._password
        )
        
        mycursor = mydb.cursor()
        mycursor.execute("SHOW DATABASES")

        for x in mycursor:
            print(x)


    """Inserts one or more data entries in a specified table"""
    def insert(self, tableName: str, header: list[str], values: tuple) -> dict:
        mydb = mysql.connector.connect(
            host=self._host,
            user=self._user,
            password=self._password,
            database=self._database
        )

        mycursor = mydb.cursor()

        headerStr= ""
        valueStr = ""
        if type(values) == tuple:
            for head in header:
                    valueStr += "%s,"
                    headerStr += head + ","

            headerStr = headerStr[: len(headerStr)-1] 
            valueStr = valueStr[: len(valueStr)-1] 
            tmp_tuple = values
        else:
            headerStr = header[0]
            valueStr = "%s"
            tmp_list: list = [values]
            tmp_tuple: tuple = tuple(tmp_list)

        sql = f"INSERT INTO {tableName} ({headerStr}) VALUES ({valueStr})"

        try:
            mycursor.execute(sql, tmp_tuple)
            mydb.commit()
            return {'result':True,'message':f"Insert in Table<{tableName}> successfull"}
        except Exception as error:
            return {'result':False,'message':error}


    """Update one or more data entries in a specified table, based on the condition statement"""
    def update(self, tableName: str, header: list[str], values: tuple, condition: str) -> dict:
        mydb = mysql.connector.connect(
            host=self._host,
            user=self._user,
            password=self._password,
            database=self._database
        )
            
        mycursor = mydb.cursor()

        valueStr = ""
        updatePair = ""
        if type(values) == tuple:
            for i in range(0, len(header)):   
                try:
                    valueStr =  str(float(values[i]))
                except ValueError: # if it is not an INT or FLOAT
                    valueStr = "'" + str(values[i]) + "'" 
                updatePair += header[i] + " = " + valueStr + ", "
        else:
            try:
                valueStr =  str(float(values))
            except ValueError: # if it is not an INT or FLOAT
                valueStr = "'" + str(values) + "'" 
            updatePair += header[0] + " = " + valueStr + ", "

        updatePair = updatePair[: len(updatePair)-2]  
        sql = f"UPDATE {tableName} SET {updatePair} WHERE {condition}"

        try:
            mycursor.execute(sql)
            mydb.commit()
            return {'result': True, 'message': f"Update in Table<{tableName}> successfull"}
        except Exception as error:
            return {'result': False, 'message': error}
        

    """Retrives one or more date entries in the specified table, based on the condition statement"""
    def select(self, tableName: str, header: str, condition: str = None) -> list:

        mydb = mysql.connector.connect(
            host=self._host,
            user=self._user,
            password=self._password,
            database=self._database
        )
            
        mycursor = mydb.cursor()

        query: str = ""
        try:
            if condition == None:
                query = f"SELECT {header} FROM {tableName}"
                #mycursor.execute(f"SELECT {header} FROM {tableName}")
            else:
                query = f"SELECT {header} FROM {tableName} WHERE {condition}"
                #mycursor.execute(f"SELECT {header} FROM {tableName} WHERE {condition}")

            mycursor.execute(query)
            result = mycursor.fetchall()
            if len(result) > 0:
                return {'result': result, 'message': 'Query successfull'}
            else:
                return {'result': None, 'message': f"No results from query <{query}>"}
        except Exception as error:
            print(error)
            return {'result': None, 'message': error}

        
    