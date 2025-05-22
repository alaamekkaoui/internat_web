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
                capacity = data.get('capacity')
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
                capacity = data.get('capacity')
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
        return result[0]['count'] if result else 0

    def set_room_used_status(self, room_number):
        """Update the is_used status of a room based on current student count and capacity."""
        # Get room info
        self.cursor.execute(f"SELECT room_type, capacity FROM {self.table_name} WHERE room_number = %s", (room_number,))
        room = self.cursor.fetchone()
        if not room:
            return False
        room_type, capacity = room[0], room[1]
        # Count students assigned to this room
        from database.db import execute_query
        query = "SELECT COUNT(*) as count FROM students WHERE num_chambre = %s"
        result = execute_query(query, (room_number,))
        student_count = result[0]['count'] if result else 0
        # Update is_used: True if full, False otherwise
        is_used = student_count >= capacity
        update_query = f"UPDATE {self.table_name} SET is_used = %s WHERE room_number = %s"
        self.cursor.execute(update_query, (is_used, room_number))
        self.conn.commit()
        return is_used

    def unassign_student_from_room(self, student_id):
        """Unassign a student from their room and update room usage status."""
        # Get the student's current room
        from database.db import execute_query
        query = "SELECT num_chambre FROM students WHERE id = %s"
        result = execute_query(query, (student_id,))
        if not result or not result[0]['num_chambre']:
            return False
        room_number = result[0]['num_chambre']
        # Unassign the student
        update_student_query = "UPDATE students SET num_chambre = 'no room' WHERE id = %s"
        self.cursor.execute(update_student_query, (student_id,))
        self.conn.commit()
        # Update room usage
        self.set_room_used_status(room_number)
        return True
