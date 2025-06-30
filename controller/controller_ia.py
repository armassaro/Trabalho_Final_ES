from models.model_ia import IAModel
from view import interface_principal

class IAController:
    """
    Controller: Orquestra o fluxo de dados entre o Model e a View.
    """
    def __init__(self, model: IAModel, view: interface_principal):
        self.model = model
        self.view = view
