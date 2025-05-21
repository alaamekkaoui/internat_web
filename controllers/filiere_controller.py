# controllers/filiere_controller.py
from models.filiere import Filiere

class FiliereController:
    def __init__(self):
        self.filiere_model = Filiere()

    def list_filieres(self):
        try:
            filiere = self.filiere_model.get_all_filieres()
            print(filiere)
            if not filiere:
                raise Exception('No filieres found')
            return filiere
        except Exception as e:
            raise Exception(str(e))

    def add_filiere(self, data):
        try:
            return self.filiere_model.add_filiere(data)
        except Exception as e:
            raise Exception(str(e))

    def get_filiere(self, filiere_id):
        try:
            return self.filiere_model.get_filiere(filiere_id)
        except Exception as e:
            raise Exception(str(e))

    def update_filiere(self, filiere_id, data):
        try:
            return self.filiere_model.update_filiere(filiere_id, data)
        except Exception as e:
            raise Exception(str(e))

    def delete_filiere(self, filiere_id):
        try:
            return self.filiere_model.delete_filiere(filiere_id)
        except Exception as e:
            raise Exception(str(e))
