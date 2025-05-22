# models/room.py
from database.db import get_connection
from datetime import datetime

class Room:
    def __init__(self):
        self.table_name = 'rooms'
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def __del__(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def get_all_rooms(self):
        """Get all rooms from the database."""
        try:
            self.cursor.execute(f"SELECT * FROM {self.table_name}")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting all rooms: {e}")
            return []

    def get_room(self, room_id):
        try:
            self.cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = %s", (room_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting room by ID: {e}")
            return None

    def add_room(self, data):
        try:
            if isinstance(data, dict):
                room_number = data.get('room_number')
                pavilion = data.get('pavilion')
                room_type = data.get('room_type')
                # Normalize room_type
                if isinstance(room_type, str):
                    room_type = room_type.strip().lower()
                if room_type == 'simple':
                    capacity = 1
                elif room_type == 'double':
                    capacity = 2
                elif room_type == 'triple':
                    capacity = 3
                else:
                    raise Exception(f"Type de chambre inconnu: {room_type}")
                print(f"add_room called with: {data} (parsed: room_number={room_number}, pavilion={pavilion}, room_type={room_type}, capacity={capacity})")
            else:
                raise Exception('Invalid data format for room')
            if not all([room_number, pavilion, room_type, capacity]):
                raise Exception('Missing required fields')
            query = f"INSERT INTO {self.table_name} (room_number, pavilion, room_type, capacity, is_used) VALUES (%s, %s, %s, %s, 0)"
            print(f"Executing SQL: {query} with values: {room_number}, {pavilion}, {room_type}, {capacity}")
            self.cursor.execute(query, (room_number, pavilion, room_type, capacity))
            self.conn.commit()
            print(f"Inserted room with room_number: {room_number}")
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Database error in add_room: {e}")
            self.conn.rollback()
            raise Exception(str(e))

    def update_room(self, room_id, data):
        try:
            if isinstance(data, dict):
                room_number = data.get('room_number')
                pavilion = data.get('pavilion')
                room_type = data.get('room_type')
                # Set capacity based on room_type
                if room_type == 'simple':
                    capacity = 1
                elif room_type == 'double':
                    capacity = 2
                elif room_type == 'triple':
                    capacity = 3
                else:
                    raise Exception('Type de chambre inconnu')
                is_used = data.get('is_used', 0)
            else:
                raise Exception('Invalid data format for room')
            if not all([room_number, pavilion, room_type, capacity]):
                raise Exception('Missing required fields')
            query = f"UPDATE {self.table_name} SET room_number = %s, pavilion = %s, room_type = %s, capacity = %s, is_used = %s WHERE id = %s"
            self.cursor.execute(query, (room_number, pavilion, room_type, capacity, is_used, room_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating room: {e}")
            self.conn.rollback()
            raise Exception(str(e))

    def delete_room(self, room_id):
        try:
            self.cursor.execute(f"DELETE FROM {self.table_name} WHERE id = %s", (room_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting room: {e}")
            self.conn.rollback()
            raise Exception(str(e))

    def get_student_count_in_room(self, room_number):
        """Return the number of students assigned to a room."""
        from database.db import execute_query
        query = "SELECT COUNT(*) as count FROM students WHERE num_chambre = %s"
        result = execute_query(query, (room_number,))
        if isinstance(result, list) and result:
            return result[0]['count']
        return 0

    def set_room_used_status(self, room_number):
        """Update the is_used status of a room based on current student count and capacity."""
        self.cursor.execute(f"SELECT room_type, capacity FROM {self.table_name} WHERE room_number = %s", (room_number,))
        room = self.cursor.fetchone()
        if not room:
            return False
        # Support both tuple and dict cursor results
        if isinstance(room, dict):
            capacity = room.get('capacity')
        else:
            capacity = room[1]
        # Defensive: ensure capacity is int
        try:
            capacity = int(capacity)
        except Exception:
            capacity = 1
        from database.db import execute_query
        query = "SELECT COUNT(*) as count FROM students WHERE num_chambre = %s"
        result = execute_query(query, (room_number,))
        student_count = result[0]['count'] if isinstance(result, list) and result and 'count' in result[0] else 0
        is_used = int(student_count) >= int(capacity)
        update_query = f"UPDATE {self.table_name} SET is_used = %s WHERE room_number = %s"
        self.cursor.execute(update_query, (is_used, room_number))
        self.conn.commit()
        return is_used

    def get_room_by_student(self, student_id):
        """Get the room number assigned to a student."""
        from database.db import execute_query
        query = "SELECT num_chambre FROM students WHERE id = %s"
        result = execute_query(query, (student_id,))
        if isinstance(result, list) and result and result[0].get('num_chambre'):
            return result[0]['num_chambre']
        return None

    def clear_student_room(self, student_id):
        """Unassign a student from their room."""
        update_student_query = "UPDATE students SET num_chambre = 'no room' WHERE id = %s"
        self.cursor.execute(update_student_query, (student_id,))
        self.conn.commit()

    def get_available_rooms(self):
        """Return a list of rooms that are not fully used (is_used = 0)."""
        try:
            self.cursor.execute(f"SELECT * FROM {self.table_name} WHERE is_used = 0")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting available rooms: {e}")
            return []
