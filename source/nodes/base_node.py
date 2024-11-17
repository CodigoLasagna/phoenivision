class BaseNode:
    def __init__(self, parent, tag):
        self.parent = parent
        self.connected_input_nodes = {}
        self.connected_output_nodes = {}
        self.tag = tag

    def create_node(self):
        """Método que debe ser implementado en las subclases"""
        raise NotImplementedError("Este método debe ser implementado en la subclase")

    def update_output_atts(self):
        """Método para actualizar texturas en nodos conectados (puede sobrescribirse)"""
        pass
