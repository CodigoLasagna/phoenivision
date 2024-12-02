import threading
import dearpygui.dearpygui as dpg

from enum import Enum

class NodeType(Enum):
    WEBCAM_BASE_NODE = 0
    PATTER_REC_NODE = 1
    DATA_PROC_NODE = 2

class BaseNode:
    def __init__(self, parent, tag, unique_id):
        self.parent = parent
        self.connected_input_nodes = {}
        self.connected_output_nodes = {}
        self.own_inputs = []
        self.own_outputs = []
        self.lock = threading.Lock()
        self.tag = tag
        self.update_loop = False
        self.node_input_data = None
        self.node_output_data = None
        self.node_type = 0
        self.children_tags = []
        self.node_unique_id = unique_id

    def create_node(self):
        """Método que debe ser implementado en las subclases"""
        raise NotImplementedError("Este método debe ser implementado en la subclase")

    def update_output_atts(self):
        """Método para actualizar texturas en nodos conectados (puede sobrescribirse)"""
        pass

    def clear_self(self):
        for ctag in self.children_tags:
            dpg.delete_item(ctag)
