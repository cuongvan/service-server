DEBUG = True
PORT = 80
OPENFAAS_GATEWAY = 'http://localhost:8080'
EXEC_TIMEOUT = 10    # seconds, first time can be slow!

# MySQL database
MYSQL_CONF = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': 'admin',
}
TABLE_NAME = 'outs'

