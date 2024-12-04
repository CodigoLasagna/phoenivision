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
                with dpg.child_window(tag=self.tag+"extra_panel", width=550, height=550):
                    pass
                dpg.bind_item_theme(self.tag+"extra_panel", Themer.create_color_window_theme())

        with dpg.plot(label=" ", parent=self.tag+"extra_panel", width=500, height=500, tag=self.tag+"matrix_container_plot"):
            dpg.add_plot_axis(dpg.mvXAxis, tag=self.tag+"matrix_container", no_label=True, no_tick_marks=True, no_tick_labels=True)
            dpg.add_plot_axis(dpg.mvYAxis, label=" ", no_tick_marks=True, no_tick_labels=True)

    def update_input_atts(self):
        recovered_data = []
        if (len(self.connected_input_nodes.values()) > 0):
            recovered_data = list(self.connected_input_nodes.values())[0].conf_matrix
            labels = list(self.connected_input_nodes.values())[0].unique_values
        if (recovered_data is not None and len(recovered_data) >= 4):
            self.received_tracked_data = recovered_data

            if (len(recovered_data[0]) >= 4):
                self.update_matrix(recovered_data, labels)

    def update_matrix(self, data, labels):
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
            with dpg.plot_axis(dpg.mvYAxis, label="Predicted Labels", parent=self.tag+"matrix_container_plot", no_tick_marks=True, no_tick_labels=True):
                for i, label in enumerate(labels):
                    dpg.add_text(label, pos=(i * 100, 0))
            with dpg.plot_axis(dpg.mvXAxis, label="True Labels", parent=self.tag+"matrix_container_plot", no_tick_marks=True, no_tick_labels=True):
                for i, label in enumerate(labels):
                    dpg.add_text(label, pos=(0, i * 100))
        else:
            dpg.configure_item(self.tag+"conf_matrix_plot", x=flat_data)

        time.sleep(0.005)

    def update_output_atts(self, stop_thread):
        if (self.update_loop == True):
            return
        self.update_loop = True
        while not(stop_thread.is_set()):
            pass
            if not(self.lock):
                break
        self.update_loop = False

class PrecisionGraphComparatorNode(BN.BaseNode):
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
        self.current_data_linear = []
        self.max_data_points = 100
        self.current_pos_track = []
        self.cur_pos_graph = 0


    def create_node(self):
        if (dpg.does_item_exist(self.tag)):
            return
        with dpg.node(label="PrecisionGraphComparatorNode", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="input_att", attribute_type=dpg.mvNode_Attr_Input, tag=self.tag+"_in_tag"):
                dpg.add_text("Data input")
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.child_window(tag=self.tag+"extra_panel", width=550, height=550):
                    pass
                dpg.bind_item_theme(self.tag+"extra_panel", Themer.create_color_window_theme())

        with dpg.plot(label=" ", parent=self.tag+"extra_panel", width=500, height=500):
            dpg.add_plot_axis(dpg.mvXAxis, label="Time")
            dpg.add_plot_axis(dpg.mvYAxis, label="Value", tag=self.tag+"value_axis_line")

    def update_input_atts(self):
        recovered_data = []
        if (len(self.connected_input_nodes.values()) > 0):
            recovered_data = list(self.connected_input_nodes.values())[0].current_prec_per
            #labels = list(self.connected_input_nodes.values())[0].unique_values
            self.received_tracked_data = float(recovered_data)

            self.update_graph()

    def update_graph(self):
        if not (dpg.does_item_exist(self.tag+"_continuous_reg")):
            dpg.add_line_series(self.current_data_linear, y=self.current_pos_track, tag=self.tag+"_continuous_reg", parent=self.tag+"value_axis_line", shaded=True)
            #dpg.set_axis_limits(self.tag+"_x_axis_scatter", 1, 0)
            dpg.set_axis_limits(self.tag+"value_axis_line", 2, -0.1)
        else:
            self.cur_pos_graph += 0.01
            self.current_pos_track.append(float(self.cur_pos_graph))
            new_data_point = (float(self.received_tracked_data))
            self.current_data_linear.append(float(new_data_point))

            dpg.configure_item(self.tag+"_continuous_reg", x=self.current_pos_track, y=self.current_data_linear)
            if (len(self.current_data_linear) > self.max_data_points):
                self.current_data_linear = []
                self.current_pos_track = []
                self.cur_pos_graph = 0

        time.sleep(0.05)

    def update_output_atts(self, stop_thread):
        if (self.update_loop == True):
            return
        self.update_loop = True
        while not(stop_thread.is_set()):
            pass
            if not(self.lock):
                break
        self.update_loop = False
