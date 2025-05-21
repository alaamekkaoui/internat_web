# controllers/room_controller.py
from models.room import Room

class RoomController:
    def __init__(self):
        self.room_model = Room()

    def list_rooms(self):
        try:
            return self.room_model.get_all_rooms()
        except Exception as e:
            raise Exception(str(e))

    def add_room(self, data):
        try:
            return self.room_model.add_room(data)
        except Exception as e:
            raise Exception(str(e))

    def get_room(self, room_id):
        try:
            return self.room_model.get_room(room_id)
        except Exception as e:
            raise Exception(str(e))

    def update_room(self, room_id, data):
        try:
            return self.room_model.update_room(room_id, data)
        except Exception as e:
            raise Exception(str(e))

    def delete_room(self, room_id):
        try:
            return self.room_model.delete_room(room_id)
        except Exception as e:
            raise Exception(str(e))
