import mysql.connector


class connector(object):
    def __init__(self, account):
        self.account = account


    def __enter__(self):
        self.connect = mysql.connector.connect(
            db = self.account["db"],
            host = self.account["host"],
            user = self.account["user"],
            passwd = self.account["passwd"],
            charset = "utf8")
        return self.connect


    def __exit__(self, exception_type, exception_value, traceback):
        self.connect.commit()
        self.connect.close()

