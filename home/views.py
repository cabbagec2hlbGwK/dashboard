from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import pymysql, os, json, boto3
from pymysql.err import OperationalError, ProgrammingError


class DcDatabase:
    def __init__(
        self,
        secret,
        endpoint,
        dbName,
        firebaseConnector,
        port=3306,
        timeout=5,
        dbTableName="approval_state_dev",
    ):
        self.endpoint = endpoint
        self.secret = secret
        self.dbName = dbName
        self.port = port
        self.timeout = timeout
        self.tableName = dbTableName
        self.firebaseConnector = firebaseConnector
        try:
            self.connection = self.DbConnect()
        except OperationalError as e:
            error_code = e.args[0]
            if error_code == 1049:
                print("the database was not found creating it and trying again")
                if self.CreateDB(self.dbName):
                    self.connection = self.DbConnect()
            print(e)

    def getAllRequestsSum(self):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {self.tableName};")
        total_sum = cursor.fetchone()[0]
        cursor.close()
        return total_sum

    def getApprovedRequestsSum(self):
        cursor = self.connection.cursor()
        cursor.execute(
            f"SELECT COUNT(*) FROM {self.tableName} WHERE approvalState = 'approved';"
        )
        approved_sum = cursor.fetchone()[0]
        cursor.close()
        return approved_sum

    def getDeniedRequestsSum(self):
        cursor = self.connection.cursor()
        cursor.execute(
            f"SELECT COUNT(*) FROM {self.tableName} WHERE approvalState = 'denied';"
        )
        denied_sum = cursor.fetchone()[0]
        cursor.close()
        return denied_sum

    def getExpireddMessagesSum(self):
        cursor = self.connection.cursor()
        cursor.execute(
            f"SELECT COUNT(*) FROM {self.tableName} WHERE approvalState = 'expired';"
        )
        rejected_sum = cursor.fetchone()[0]
        cursor.close()
        return rejected_sum

    def getActiveMessagesSum(self):
        cursor = self.connection.cursor()
        cursor.execute(
            f"SELECT COUNT(*) FROM {self.tableName} WHERE approvalState = 'active';"
        )
        rejected_sum = cursor.fetchone()[0]
        cursor.close()
        return rejected_sum

    def DbConnect(self):
        connection = pymysql.connect(
            host=self.endpoint,
            user=self.secret["username"],
            password=self.secret["password"],
            db=self.dbName,
            port=self.port,
            connect_timeout=self.timeout,
        )
        print("Connection successful")
        return connection

    def CreateDB(self, dbName):
        connection = pymysql.connect(
            host=self.endpoint,
            user=self.secret["username"],
            password=self.secret["password"],
            port=self.port,
            connect_timeout=self.timeout,
        )
        print("Connection successful")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE {dbName}")
                print(f"Database {dbName} created successfully.")
                connection.commit()
        except pymysql.MySQLError as e:
            print(f"Failed to create database: {str(e)}")
            connection.close()
            return False
        connection.close()
        return True

    def close(self):
        self.connection.close()

    def dbIfExist(self):
        cursor = self.connection.cursor()
        cursor.execute(f"SHOW DATABASES LIKE '{self.dbName}'")

        result = cursor.fetchone()
        if not result:
            print(f"Database {self.dbName} does not exist. Creating database.")
            cursor.execute(f"CREATE DATABASE {self.dbName}")
            self.connection.commit()
        else:
            print(f"Database {self.dbName} already exists.")

        cursor.close()

    def searchData(self, string):
        cursor = self.connection.cursor()
        query = f"SELECT approvalState, sender, reciver, user, timeStamp, messageId, approvalTime FROM {self.tableName} WHERE sender LIKE '%{string}%' OR reciver LIKE '%{string}%' OR user LIKE '%{string}%';"
        cursor.execute(query)

        rows = cursor.fetchall()
        records = []

        for row in rows:
            # Create a dictionary with the required fields
            record = {
                "approvalState": row[0],
                "sender": row[1],
                "reciver": row[2],
                "user": json.loads(row[3]),
                "timeStamp": row[4],
                "messageId": row[5],
                "approvalTime": row[6],
            }
            # Append each dictionary to the list
            records.append(record)
        cursor.close()
        return records

    def getData(self, messageId=""):
        if messageId != "":
            clause = f"WHERE messageId = '{messageId}'"
        else:
            clause = ""
        cursor = self.connection.cursor()
        query = f"SELECT approvalState, sender, reciver, user, timeStamp, messageId, approvalState, pii, approvalTime FROM {self.tableName} {clause} ORDER BY timeStamp DESC LIMIT 50;"
        cursor.execute(query)

        rows = cursor.fetchall()
        records = []

        for row in rows:
            # Create a dictionary with the required fields
            record = {
                "approvalState": row[0],
                "sender": row[1],
                "reciver": row[2],
                "user": json.loads(row[3]),
                "timeStamp": row[4],
                "messageId": row[5],
                "state": row[6],
                "pii": json.loads(row[7]),
                "approvalTime": row[8],
            }
            # Append each dictionary to the list
            records.append(record)
        cursor.close()
        return records


def get_secret(secret_name):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager")

    try:
        print("trying value")
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        print("ther was a error :" + str(e))

    secret = get_secret_value_response["SecretString"]
    print("the is " + str(secret_name))
    return secret


def getConnection():
    secretName = os.getenv("secret_name")
    rdsEndpoint = os.getenv("rds_endpoint")
    tableN = os.getenv("tableName")
    rdsSec = json.loads(get_secret(secretName))
    db = DcDatabase(
        secret=rdsSec,
        endpoint=rdsEndpoint,
        dbName="test1",
        firebaseConnector=None,
        dbTableName=tableN,
    )
    return db


def home(res):
    if not res.user.is_authenticated:
        messages.error(res, "Access denied please login in again")
        return redirect("login")
    DB_CONNECTION = getConnection()
    totalMessages = DB_CONNECTION.getAllRequestsSum()
    totalApproved = DB_CONNECTION.getApprovedRequestsSum()
    totalDeny = DB_CONNECTION.getDeniedRequestsSum()
    totalExpired = DB_CONNECTION.getExpireddMessagesSum()
    totalActive = DB_CONNECTION.getActiveMessagesSum()
    data = DB_CONNECTION.getData()
    values = {
        "message": totalMessages,
        "approved": totalApproved,
        "deny": totalDeny,
        "expired": totalExpired,
        "active": totalActive,
        "data": data,
    }
    DB_CONNECTION.close()
    del DB_CONNECTION
    return render(res, "dash.html", {"items": values})


def search(res):
    if not res.user.is_authenticated:
        messages.error(res, "Access denied please login in again")
        return redirect("login")
    DB_CONNECTION = getConnection()
    string = res.GET.get("search")
    print(string)
    data = DB_CONNECTION.searchData(string)
    values = {"data": data}
    DB_CONNECTION.close()
    del DB_CONNECTION
    return render(res, "results.html", {"items": values})


def logoutUser(res):
    logout(res)
    messages.success(res, "Sucessfully logout")
    return redirect("login")


# Create your views here.
def loginUser(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "invalid credintials")
            return redirect("login")
    else:
        return render(request, "login.html", {})


def getMessage(res):
    if not res.user.is_authenticated:
        messages.error(res, "Access denied please login in again")
        return redirect("login")
    DB_CONNECTION = getConnection()
    messageId = res.GET.get("messageId")
    data = DB_CONNECTION.getData(messageId=messageId)
    values = {"data": data}
    DB_CONNECTION.close()
    del DB_CONNECTION
    return render(res, "message.html", {"items": values})
