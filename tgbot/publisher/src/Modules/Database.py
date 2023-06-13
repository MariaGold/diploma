from psycopg2 import connect

class Database:
    def __init__(self):
        self.conn = self.connect_db()

    def connect_db(self):
        conn = connect(
            host='postgres',
            dbname='stdb',
            user='maria',
            password='123456'
        )

        return conn
    
    def add_user_command(self, user_id, command):
        pass

    def get_user_stats(self, user_id):
        pass