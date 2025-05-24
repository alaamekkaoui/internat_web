# models/room.py
from database.db import get_connection
from datetime import datetime
import pymysql

class Room:
    def __init__(self):
        self.table_name = 'rooms'
        self.conn = get_connection()
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)

    def __del__(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def get_all_rooms(self):
        """Get all rooms from the database."""
        try:
            self.cursor.execute("""
                SELECT r.*, 
                       (SELECT COUNT(*) FROM students s WHERE s.num_chambre = r.room_number) as used_capacity
                FROM rooms r
                ORDER BY r.room_number
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"[ERROR] get_all_rooms: {e}")
            return []

    def get_room_by_number(self, room_number):
        try:
            self.cursor.execute("""
                SELECT r.*, 
                       (SELECT COUNT(*) FROM students s WHERE s.num_chambre = r.room_number) as used_capacity
                FROM rooms r
                WHERE r.room_number = %s
            """, (room_number,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"[ERROR] get_room_by_number: {e}")
            return None

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
                
                # Strict room type validation
                if room_type not in ['single', 'double', 'triple']:
                    raise Exception(f"Type de chambre invalide: {room_type}. Doit être 'single', 'double' ou 'triple'")
                
                # Set capacity based on room_type
                if room_type == 'single':
                    capacity = 1
                elif room_type == 'double':
                    capacity = 2
                elif room_type == 'triple':
                    capacity = 3
                
                # Override any provided capacity to match room type
                data['capacity'] = capacity
                
                print(f"add_room called with: {data} (parsed: room_number={room_number}, pavilion={pavilion}, room_type={room_type}, capacity={capacity})")
            else:
                raise Exception('Invalid data format for room')
                
            if not all([room_number, pavilion, room_type]):
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
                
                # Normalize room_type
                if isinstance(room_type, str):
                    room_type = room_type.strip().lower()
                
                # Strict room type validation
                if room_type not in ['single', 'double', 'triple']:
                    raise Exception(f"Type de chambre invalide: {room_type}. Doit être 'single', 'double' ou 'triple'")
                
                # Set capacity based on room_type
                if room_type == 'single':
                    capacity = 1
                elif room_type == 'double':
                    capacity = 2
                elif room_type == 'triple':
                    capacity = 3
                
                # Override any provided capacity to match room type
                data['capacity'] = capacity
                is_used = data.get('is_used', 0)
            else:
                raise Exception('Invalid data format for room')
                
            if not all([room_number, pavilion, room_type]):
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

    def delete_room_by_number(self, room_number):
        try:
            self.cursor.execute(f"DELETE FROM {self.table_name} WHERE room_number = %s", (room_number,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting room by number: {e}")
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
        """Update room's used status based on current student count"""
        try:
            # Get room details
            self.cursor.execute("""
                SELECT r.*, COUNT(s.id) as student_count
                FROM rooms r
                LEFT JOIN students s ON r.room_number = s.num_chambre
                WHERE r.room_number = %s
                GROUP BY r.room_number
            """, (room_number,))
            room = self.cursor.fetchone()
            
            if not room:
                print(f"[ERROR] Room {room_number} not found")
                return False
            
            # Calculate if room is used
            student_count = room['student_count'] if room['student_count'] is not None else 0
            capacity = room['capacity']
            is_used = int(student_count) == int(capacity)
            
            # Update room status
            self.cursor.execute("""
                UPDATE rooms 
                SET is_used = %s,
                    updated_at = NOW()
                WHERE room_number = %s
            """, (is_used, room_number))
            self.conn.commit()
            
            print(f"[INFO] Room {room_number} status updated: {is_used} (students: {student_count}/{capacity})")
            return True
        except Exception as e:
            print(f"[ERROR] set_room_used_status: {e}")
            self.conn.rollback()
            return False

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
        """Get list of available rooms"""
        try:
            self.cursor.execute("""
                SELECT r.*, COUNT(s.id) as current_students
                FROM rooms r
                LEFT JOIN students s ON r.room_number = s.num_chambre
                GROUP BY r.room_number
                HAVING current_students < r.capacity OR current_students IS NULL
                ORDER BY r.room_number
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"[ERROR] get_available_rooms: {e}")
            return []
