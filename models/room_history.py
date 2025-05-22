from database.db import get_connection, execute_query
from datetime import datetime

class RoomHistory:
    def __init__(self):
        self.table_name = 'room_history'
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def __del__(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def add_history(self, student_id, room_number, year=None):
        """Add a room assignment to the history table."""
        if not year:
            year = datetime.now().year
        query = f"INSERT INTO {self.table_name} (student_id, room_number, year) VALUES (%s, %s, %s)"
        self.cursor.execute(query, (student_id, room_number, year))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_history_for_student(self, student_id):
        query = f"SELECT * FROM {self.table_name} WHERE student_id = %s ORDER BY year DESC"
        self.cursor.execute(query, (student_id,))
        return self.cursor.fetchall()
