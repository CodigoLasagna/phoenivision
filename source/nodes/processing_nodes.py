
import dearpygui.dearpygui as dpg
#import numpy as np
from . import base_node as BN
from ..theming.base_theme_confs import Themer
#import cv2 as cv
import numpy as np
import time
from pathlib import Path

class StaticDatabaseManagerNode(BN.BaseNode):
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
        self.database_dir = Path("./app_data/databases")
        self.current_data_type = 0


    def create_node(self):
        if (dpg.does_item_exist(self.tag)):
            return
        with dpg.node(label="StaticDatabaseManagerNode", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="input_att", attribute_type=dpg.mvNode_Attr_Input, tag=self.tag+"_in_tag"):
                dpg.add_text("Data input")
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.child(tag=self.tag+"extra_panel", width=570, height=700):
                    pass
                dpg.bind_item_theme(self.tag+"extra_panel", Themer.create_color_window_theme())

            with dpg.node_attribute(label="output_att", attribute_type=dpg.mvNode_Attr_Output, tag=self.tag+"_out_tag"):
                dpg.add_text("Data output")
        self.gen_extra_items()

    def gen_extra_items(self):
        dpg.add_radio_button(
            parent=self.tag + "extra_panel",
            items=["Nueva DB", "Cargar DB"],
            horizontal=True,
            callback=self.toggle_sections,
            tag=self.tag + "data_col_radio"
        )
        
        # Grupo para "Nuevo modelo"
        with dpg.group(parent=self.tag + "extra_panel", tag=self.tag + "extra_panel_radio_new_model", show=True, height=35):
            with dpg.table(header_row=False):
                dpg.add_table_column(width_fixed=True)
                dpg.add_table_column(width_fixed=True)

                with dpg.table_row():
                    dpg.add_text("DB Nombre: ")
                    dpg.add_input_text(width=300)

                with dpg.table_row():
                    dpg.add_text("Etiqueta: ")
                    dpg.add_input_text(width=300)

                with dpg.table_row():
                    dpg.add_text("No. Snapshots: ")
                    dpg.add_input_int(width=300)
            temp_item = dpg.add_button(label="Capturar datos")
        
        # Grupo para "Cargar modelo"
        with dpg.group(parent=self.tag + "extra_panel", tag=self.tag + "extra_panel_radio_load_model", show=False):
            dpg.add_combo(
                default_value="Cargar DB",
                items=["Eliminar"],
                callback=lambda sender: print(dpg.get_value(sender)),
                tag=self.tag+"extra_panel_db_combo"
            ),

        #with dpg.group(parent=self.tag+"extra_panel", height=35, width=200, tag="test_group"):
        with dpg.plot(label="Gráfico general", parent=self.tag+"extra_panel", width=500, height=500):
            dpg.add_plot_axis(dpg.mvXAxis, label="X", tag="x_axis_scatter")
            dpg.add_plot_axis(dpg.mvYAxis, label="Y", tag="y_axis_scatter")

        dpg.bind_item_theme(temp_item, Themer.create_green_btn_theme())
    def load_existing_databases(self):
        csv_dbs = [file.name for file in self.database_dir.iterdir() if file.suffix == '.csv']
        dpg.configure_item(self.tag+"extra_panel_db_combo", items=csv_dbs)
        #print(csv_dbs)

    
    def toggle_sections(self, sender, app_data):
        if app_data == "Nueva DB":
            dpg.configure_item(self.tag + "extra_panel_radio_new_model", show=True)
            dpg.configure_item(self.tag + "extra_panel_radio_load_model", show=False)
        else:
            dpg.configure_item(self.tag + "extra_panel_radio_new_model", show=False)
            dpg.configure_item(self.tag + "extra_panel_radio_load_model", show=True)
            self.load_existing_databases()


    def update_input_atts(self):
        recovered_data = []
        if (len(self.connected_input_nodes.values()) > 0):
            recovered_data = list(self.connected_input_nodes.values())[0].node_output_data
        if (len(recovered_data) > 0):
            if (self.current_data_type != recovered_data[0]):
                self.current_data_type = recovered_data[0]
            self.update_plot(recovered_data[0], recovered_data[1])

    def update_plot(self, data_type, data):
        #print(data_type)
        #print(data)
        if data_type == 0:
            dpg.set_axis_limits("x_axis_scatter", 1, 0)
            dpg.set_axis_limits("y_axis_scatter", -1, 0)
            x_vals = []
            y_vals = []
            for i, dataset in enumerate(data):
                # Filtrar los puntos válidos
                valid_points = [
                    point for point in dataset
                    if isinstance(point, (list, tuple)) and len(point) == 3 and
                    not any(p is None or (isinstance(p, float) and np.isnan(p)) for p in point)
                ]
                
                # Extraer valores x y y de los puntos válidos
                x_vals.extend([point[0] for point in valid_points])
                y_vals.extend([-point[1] for point in valid_points])
        
                # Agregar la serie al gráfico
                #dpg.add_scatter_series(parent="x_axis_scatter", x=x_vals, y=y_vals, label=f"serie {i + 1}")
            if (len(x_vals) > 0):
                if not (dpg.does_item_exist("hands_cloud_points")):
                    dpg.add_scatter_series(parent="x_axis_scatter", x=x_vals, y=y_vals, label=f"serie {i + 1}", tag="hands_cloud_points")
                else:
                    dpg.configure_item("hands_cloud_points", x=x_vals, y=y_vals, label=f"serie {i + 1}")
            else:
                if (dpg.does_item_exist("hands_cloud_points")):
                    dpg.configure_item("hands_cloud_points", x=x_vals, y=y_vals)

        time.sleep(0.01)

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
