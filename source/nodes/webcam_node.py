import dearpygui.dearpygui as dpg
import numpy as np

class WebcamOutputNode:
    def __init__(self, parent, tag):
        self.parent = parent
        self.connected_node_output = None
        self.tag = tag
        self.create_node()

    def create_node(self):
        if (dpg.does_item_exist("webcam_output_node")):
            return
        with dpg.node(label="Webcam output node", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="output_att", attribute_type=dpg.mvNode_Attr_Output, tag="won_tag"):
                dpg.add_image(texture_tag="webcam_texture", tag="image_output")

    def update_connected_node_texture():
        pass

class MediapipeInputOutputNode:
    def __init__(self, parent, tag):
        self.parent = parent
        self.connected_node_input = None
        self.connected_node_output = None
        self.tag = tag
        self.initial_texture_data = [0, 0, 0, 255] * (320 * 240)
        with dpg.texture_registry():
            self.initial_texture_id = dpg.add_static_texture(320, 240, self.initial_texture_data)
        self.create_node()

    def create_node(self):
        if (dpg.does_item_exist("mediapipe_out_in_node")):
            return
        with dpg.node(label="Mediapipa Out/In node", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="Webcam input", attribute_type=dpg.mvNode_Attr_Input, tag="moin_tag"):
                dpg.add_image(texture_tag=self.initial_texture_id, tag="image_input")

def create_node(node_class, parent, node_dictionary):
    tag = str(node_class.__name__)
    if (tag in node_dictionary):
        print("already exists")
        return

    node_dictionary[tag] = node_class(parent=parent, tag=tag)
    #print(node_dictionary[tag])
