import mysql.connector

# Singleton
import project_conf

# create a class to avoid python's week reference errors
class DBConnection:
    def __init__(self):
        self.conn = mysql.connector.connect(
            **project_conf.MYSQL_CONF,
            database='function_database')
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def insert_result(self, call_id, service, status, output):
        # TODO move table name to config
        query = ('INSERT INTO {} (call_id, service, time_done, status, output)' 
                 'VALUES (%s, %s, NOW(), %s, %s)').format(project_conf.TABLE_NAME)
        value = (call_id, service, status, output)
        self.cursor.execute(query, value)
        self.conn.commit()
