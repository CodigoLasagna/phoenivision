
import dearpygui.dearpygui as dpg
#import numpy as np
from . import base_node as BN
#import cv2 as cv
import numpy as np
import time

class DataColectorNode(BN.BaseNode):
    def __init__(self, parent, tag):
        super().__init__(parent, tag)
        self.node_type = BN.NodeType.DATA_PROC_NODE
        self.create_node()
        mouse_pos = dpg.get_mouse_pos(local=False)
        mouse_pos[0] = mouse_pos[0] - 180
        mouse_pos[1] = mouse_pos[1] - 120
        dpg.set_item_pos(self.tag, mouse_pos)
        self.children_tags.append(self.tag+"_in_tag")
        self.children_tags.append(self.tag+"_out_tag")


    def create_node(self):
        if (dpg.does_item_exist(self.tag)):
            return
        with dpg.node(label="DataColectorNode", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="input_att", attribute_type=dpg.mvNode_Attr_Input, tag=self.tag+"_in_tag"):
                dpg.add_text("Data input")
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                #with dpg.child_window(tag=self.tag+"extra_panel", width=200, height=200):
                #    pass
                with dpg.group(tag=self.tag+"extra_panel", width=200, height=200):
                    pass

            with dpg.node_attribute(label="output_att", attribute_type=dpg.mvNode_Attr_Output, tag=self.tag+"_out_tag"):
                dpg.add_text("Data output")
        self.gen_extra_items()

    def gen_extra_items(self):
        dpg.add_text(parent=self.tag+"extra_panel", default_value="Dataset Name: ")
        dpg.add_input_text(parent=self.tag+"extra_panel")
        dpg.add_combo(parent=self.tag+"extra_panel",
            default_value="algorithm",
            items=[
                "KNeighbors",
                "DecisionTree",
                "LogisticRegression",
                "LinearRegression",
                "SVC(Support Vector Classifier)",
                "GaussianNB",
                "KMeans",
                ],
            #callback=lambda sender: self.node_combo_item(node.tag, dpg.get_value(sender)),
            #tag=node"_options"
        ),


    def update_input_atts(self):
        time.sleep(0.1)

    def process_texture_data(self):
        pass


    def update_output_atts(self, stop_thread):
        if (self.update_loop == True):
            return
        self.update_loop = True
        while not(stop_thread.is_set()):
            pass
            if not(self.lock):
                break
        self.update_loop = False
