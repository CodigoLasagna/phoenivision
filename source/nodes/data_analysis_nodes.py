import dearpygui.dearpygui as dpg
#import numpy as np
from . import base_node as BN
from ..theming.base_theme_confs import Themer
#import cv2 as cv
import numpy as np
import time
#import csv
#from pathlib import Path

class ConfusionMatrixNode(BN.BaseNode):
    def __init__(self, parent, tag, unique_id):
        super().__init__(parent, tag, unique_id)
        self.node_type = BN.NodeType.DATA_PROC_NODE
        self.tag = self.tag + "_" + str(self.node_unique_id)
        self.create_node()
        mouse_pos = dpg.get_mouse_pos(local=False)
        mouse_pos[0] = mouse_pos[0] - 180
        mouse_pos[1] = mouse_pos[1] - 120
        dpg.set_item_pos(self.tag, mouse_pos)
        self.children_tags.append(self.tag+"_in_tag")
        self.children_tags.append(self.tag+"_out_tag")
        self.current_data_type = 0
        self.received_tracked_data = []


    def create_node(self):
        if (dpg.does_item_exist(self.tag)):
            return
        with dpg.node(label="ConfusionMatrixNode", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="input_att", attribute_type=dpg.mvNode_Attr_Input, tag=self.tag+"_in_tag"):
                dpg.add_text("Data input")
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.child_window(tag=self.tag+"extra_panel", width=530, height=530):
                    pass
                dpg.bind_item_theme(self.tag+"extra_panel", Themer.create_color_window_theme())

        #with dpg.group(parent=self.tag+"extra_panel", height=35, width=200, tag="test_group"):
        with dpg.plot(label="Gráfico general", parent=self.tag+"extra_panel", width=500, height=500):
            dpg.add_plot_axis(dpg.mvXAxis, label="X", tag=self.tag+"matrix_container")
            #dpg.add_heat_series("Confusion Matrix Heatmap", self.received_tracked_data, rows=len(self.received_tracked_data), cols=len(self.received_tracked_data))

    def update_input_atts(self):
        recovered_data = []
        if (len(self.connected_input_nodes.values()) > 0):
            recovered_data = list(self.connected_input_nodes.values())[0].conf_matrix
        #print(recovered_data)
        if (recovered_data is not None and len(recovered_data) >= 4):
            self.received_tracked_data = recovered_data

            #print(recovered_data)
            if (len(recovered_data[0]) >= 4):
                self.update_matrix(recovered_data)

    def update_matrix(self, data):
        flat_data = [item for sublist in data for item in sublist]
        #print(data)
        normal_data = data.tolist()
        min_val = min(flat_data)
        max_val = max(flat_data)
        #print(normal_data)

        if not (dpg.does_item_exist(self.tag+"conf_matrix_plot")):
            dpg.add_heat_series(
                    parent=self.tag+"matrix_container",
                    label="Confusion Matrix Heatmap",
                    x=flat_data,
                    cols=len(normal_data),
                    rows=len(normal_data[0]),
                    tag=self.tag+"conf_matrix_plot",
                    scale_min=min_val,
                    scale_max=max_val,
                    col_major=True
                )
        else:
            dpg.configure_item(self.tag+"conf_matrix_plot", x=flat_data)

        time.sleep(0.005)

    def set_color_map(self):
        colors = [
            (0.0, (0.0, 0.0, 1.0)),  # Azul para valores bajos
            (0.2, (0.0, 1.0, 1.0)),  # Cian
            (0.4, (0.0, 1.0, 0.0)),  # Verde
            (0.6, (1.0, 1.0, 0.0)),  # Amarillo
            (0.8, (1.0, 0.5, 0.0)),  # Naranja
            (1.0, (1.0, 0.0, 0.0))   # Rojo para valores altos
        ]
        return colors

    def update_output_atts(self, stop_thread):
        if (self.update_loop == True):
            return
        self.update_loop = True
        while not(stop_thread.is_set()):
            pass
            if not(self.lock):
                break
        self.update_loop = False
