
import dearpygui.dearpygui as dpg
#import numpy as np
from . import base_node as BN
from ..theming.base_theme_confs import Themer
#import cv2 as cv
import numpy as np
import time
import csv
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
        self.database_dir = "./app_data/databases"
        self.path_to_pass = ""
        self.database_open_path = Path(self.database_dir)
        self.current_data_type = 0
        self.received_tracked_data = []
        self.capturing = False


    def create_node(self):
        if (dpg.does_item_exist(self.tag)):
            return
        with dpg.node(label="StaticDatabaseManagerNode", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="input_att", attribute_type=dpg.mvNode_Attr_Input, tag=self.tag+"_in_tag"):
                dpg.add_text("Data input")
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.group(tag=self.tag+"extra_panel", width=530, height=32):
                    pass
                dpg.bind_item_theme(self.tag+"extra_panel", Themer.create_color_window_theme())
                dpg.add_button(label="Tags", width=530, tag=self.tag+"tags_table_header")
                dpg.bind_item_theme(self.tag+"tags_table_header", Themer.make_button_title())
                with dpg.table(header_row=False, width=530, height=128, scrollY=True):
                    dpg.add_table_column(width_fixed=True)

                    with dpg.table_row():
                        with dpg.group(tag=self.tag+"_tags_list", width=530, height=32):
                            pass

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
                    dpg.add_input_text(width=360, tag=self.tag+"db_name_file")

                with dpg.table_row():
                    dpg.add_text("Etiqueta: ")
                    dpg.add_input_text(width=360, tag=self.tag+"gesture_label_tag")

                with dpg.table_row():
                    dpg.add_text("Timer: ")
                    dpg.add_input_int(width=360, tag=self.tag+"timer_dur_tag")
                with dpg.table_row():
                    dpg.add_text("No. Snapshots: ")
                    dpg.add_input_int(width=360, tag=self.tag+"snapshots_take_number")
                with dpg.table_row():
                    dpg.add_text("ms entre captura: ")
                    dpg.add_input_int(width=360, tag=self.tag+"snapshots_ms_sep")

            dpg.add_button(label="status", tag=self.tag+"status_node_tag")
            dpg.bind_item_theme(self.tag+"status_node_tag", Themer.create_contour_color_text())

            temp_item = dpg.add_button(label="Crear DB", tag=self.tag+"save_db_btn", callback=self.save_database)
            dpg.bind_item_theme(self.tag+"save_db_btn", Themer.create_green_btn_theme())

            temp_item = dpg.add_button(label="Capturar datos", callback=self.save_timed_snapshots)
            dpg.bind_item_theme(temp_item, Themer.create_yellow_btn_theme())

            temp_item = dpg.add_button(label="Cargar Datos", tag=self.tag+"load_data", callback=lambda: self.load_data_from_db(loader_part=0))
            dpg.bind_item_theme(self.tag+"load_data", Themer.create_blue_btn_theme())
        
        # Grupo para "Cargar modelo"
        with dpg.group(parent=self.tag + "extra_panel", tag=self.tag + "extra_panel_radio_load_model", show=False):
            dpg.add_combo(
                default_value="Cargar DB",
                #items=["Eliminar"],
                callback=lambda sender: self.load_data_from_db(loader_part=1, csv_name=dpg.get_value(sender)),
                tag=self.tag+"extra_panel_db_combo"
            ),
    def save_database(self):
        if (len(self.connected_input_nodes.items()) < 1):
            #print("No input nodes")
            dpg.configure_item(self.tag+"status_node_tag", label="No input nodes")
            dpg.bind_item_theme(self.tag+"status_node_tag", Themer.create_contour_color_text([240, 79, 120]))
            return
        self.initialize_csv()

    def initialize_csv(self):
        fixed_file_name = dpg.get_value(self.tag+"db_name_file")
        fixed_file_name = fixed_file_name.replace(" ", "_")
        file_to_open = Path(self.database_dir+"/"+fixed_file_name+".csv")
        if (len(fixed_file_name) < 1):
            dpg.configure_item(self.tag+"status_node_tag", label="Nombre no valido")
            dpg.bind_item_theme(self.tag+"status_node_tag", Themer.create_contour_color_text([240, 79, 120]))
            return
        if not (file_to_open.exists()):
            csvfile = (open(file_to_open, 'w', newline=''))
            dpg.configure_item(self.tag+"status_node_tag", label="Base de datos registrada")
            dpg.bind_item_theme(self.tag+"status_node_tag", Themer.create_contour_color_text([127, 218, 37]))
        else:
            return
        if (self.current_data_type == 0):
            writer = csv.writer(csvfile)
            writer.writerow([self.current_data_type])
            writer.writerow(['tag', 'keypoints_left_hand', 'keypoints_right_hand'])
        if (self.current_data_type == 1):
            writer = csv.writer(csvfile)
            writer.writerow([self.current_data_type])
            writer.writerow(['tag', 'keypoints_pose'])

    def load_data_from_db(self, show_flag_messages=True, loader_part=0, csv_name=""):
        fixed_file_name = ""
        if (loader_part == 0):
            fixed_file_name = dpg.get_value(self.tag+"db_name_file")
        elif(loader_part == 1):
            fixed_file_name = csv_name.replace(".csv", '')
            dpg.set_value(self.tag+"db_name_file", fixed_file_name)
        fixed_file_name = fixed_file_name.replace(" ", "_")
        file_to_open = Path(self.database_dir+"/"+fixed_file_name+".csv")
        if (len(fixed_file_name) < 1):
            if (show_flag_messages):
                dpg.configure_item(self.tag+"status_node_tag", label="Nombre no valido")
                dpg.bind_item_theme(self.tag+"status_node_tag", Themer.create_contour_color_text([240, 79, 120]))
            return
        if not (file_to_open.exists()):
            if (show_flag_messages):
                dpg.configure_item(self.tag+"status_node_tag", label="DB no encontrado")
                dpg.bind_item_theme(self.tag+"status_node_tag", Themer.create_contour_color_text([240, 79, 120]))
            return
        self.path_to_pass = self.database_dir+"/"+fixed_file_name+".csv"
        self.node_output_data = self.path_to_pass
        db = open(file_to_open, 'r')
        db_data_type = next(db)
        reader = csv.DictReader(db)
        values = list()
        #db_data_type = 
        if (db_data_type):
            pass
            #print("db datatype: " + str(db_data_type))
        for row in reader:
            if not (row['tag'] in values):
                values.append(row['tag'])
        if (show_flag_messages):
            dpg.configure_item(self.tag+"status_node_tag", label="Datos cargados")
            dpg.bind_item_theme(self.tag+"status_node_tag", Themer.create_contour_color_text([127, 218, 37]))
        #children = dpg.get_item_children(self.tag+"tags_list")
        #print(children)
        dpg.delete_item(self.tag+"_tags_list", children_only=True)
        for val in values:
            dpg.add_text(parent=self.tag+"_tags_list", default_value=val)
        dpg.configure_item(self.tag+"tags_table_header", label="Tags: ("+str(len(values))+")")

    def load_existing_databases(self):
        csv_dbs = [file.name for file in self.database_open_path.iterdir() if file.suffix == '.csv']
        dpg.configure_item(self.tag+"extra_panel_db_combo", items=csv_dbs)

    def save_timed_snapshots(self):
        if (self.capturing):
            return
        self.capturing = True
        countdown = int(dpg.get_value(self.tag+"timer_dur_tag"))
        snapshots_n = int(dpg.get_value(self.tag+"snapshots_take_number"))
        miliseconds = float(dpg.get_value(self.tag+"snapshots_ms_sep")) / 1000
        dpg.configure_item(self.tag+"status_node_tag", label="tiempo antes de capturar: " + str(countdown))
        dpg.bind_item_theme(self.tag+"status_node_tag", Themer.create_contour_color_text())
        while(countdown > 0):
            time.sleep(1)
            countdown -=1
            dpg.configure_item(self.tag+"status_node_tag", label="tiempo antes de capturar: " + str(countdown))
            dpg.bind_item_theme(self.tag+"status_node_tag", Themer.create_contour_color_text())

        while(snapshots_n > 0):
            self.save_snapshot()
            snapshots_n -= 1
            dpg.configure_item(self.tag+"status_node_tag", label="Capturas restantes: " + str(snapshots_n))
            dpg.bind_item_theme(self.tag+"status_node_tag", Themer.create_contour_color_text())
            time.sleep(miliseconds)

        dpg.configure_item(self.tag+"status_node_tag", label="Captura finalizada")
        dpg.bind_item_theme(self.tag+"status_node_tag", Themer.create_contour_color_text([127, 218, 37]))
        self.capturing = False
        self.load_data_from_db(show_flag_messages=False)

    def save_snapshot(self):
        self.initialize_csv()
        fixed_file_name = dpg.get_value(self.tag+"db_name_file")
        fixed_file_name = fixed_file_name.replace(" ", "_")
        file_to_open = Path(self.database_dir+"/"+fixed_file_name+".csv")

        #if (self.current_data_type == 0):
        csvfile = (open(file_to_open, 'a', newline=''))
        writer = csv.writer(csvfile)
        fixed_gesture_label = dpg.get_value(self.tag+"gesture_label_tag").replace(' ', '_')
        #print(self.received_tracked_data)
        track_limit = len(self.received_tracked_data)-1
        #print(track_limit)

        #writer.writerow([fixed_gesture_label, self.received_tracked_data[0], self.received_tracked_data[1]])
        if (self.current_data_type == 0):
            writer.writerow([fixed_gesture_label, self.received_tracked_data[0], self.received_tracked_data[track_limit]])
        else:
            writer.writerow([fixed_gesture_label, self.received_tracked_data[0]])

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
        if (recovered_data == None):
            return
        if (len(recovered_data) > 0):
            if (self.current_data_type != recovered_data[0]):
                self.current_data_type = recovered_data[0]
        self.received_tracked_data = recovered_data[1]
        self.node_output_data = self.path_to_pass

        time.sleep(0.01)

    def update_output_atts(self, stop_thread):
        if (self.update_loop == True):
            return
        self.update_loop = True
        while not(stop_thread.is_set()):
            pass
            if not(self.lock):
                break
            for link_tag_name, node_instance in list(self.connected_output_nodes.items()):
                #if (node_instance.alreay_running == False):
                node_instance.update_input_atts()
            time.sleep(0.01)
        self.update_loop = False

class MultiGraphCapNode(BN.BaseNode):
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


    def create_node(self):
        if (dpg.does_item_exist(self.tag)):
            return
        with dpg.node(label="MultiGraphCapNode", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="input_att", attribute_type=dpg.mvNode_Attr_Input, tag=self.tag+"_in_tag"):
                dpg.add_text("Data input")
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.child_window(tag=self.tag+"extra_panel", width=530, height=530):
                    pass
                dpg.bind_item_theme(self.tag+"extra_panel", Themer.create_color_window_theme())

        #with dpg.group(parent=self.tag+"extra_panel", height=35, width=200, tag="test_group"):
        with dpg.plot(label="Gráfico general", parent=self.tag+"extra_panel", width=500, height=500):
            dpg.add_plot_axis(dpg.mvXAxis, label="X", tag=self.tag+"_x_axis_scatter")
            dpg.add_plot_axis(dpg.mvYAxis, label="Y", tag=self.tag+"_y_axis_scatter")

    def update_input_atts(self):
        recovered_data = []
        if (len(self.connected_input_nodes.values()) > 0):
            recovered_data = list(self.connected_input_nodes.values())[0].node_output_data
        if (len(recovered_data) > 0):
            if (self.current_data_type != recovered_data[0]):
                self.current_data_type = recovered_data[0]

            self.update_plot(recovered_data[0], recovered_data[1])

    def update_plot(self, data_type, data):
        #print(data)
        #if data_type == 0 or data_type == 1:
        dpg.set_axis_limits(self.tag+"_x_axis_scatter", 1, 0)
        dpg.set_axis_limits(self.tag+"_y_axis_scatter", -1, 0)
        x_vals = []
        y_vals = []
        for group in data:  # Iterar sobre los dos grupos de puntos
            # Filtrar los puntos válidos en el grupo
            valid_points = [
                point for point in group
                if isinstance(point, (list, tuple)) and len(point) == 3 and
                not any(p is None or (isinstance(p, float) and np.isnan(p)) for p in point)
            ]
            
            # Extraer valores x y y de los puntos válidos
            x_vals.extend([point[0] for point in valid_points])
            y_vals.extend([-point[1] for point in valid_points])
        
            # Agregar la serie al gráfico
        if (len(x_vals) > 0):
            if not (dpg.does_item_exist(self.tag+"_hands_cloud_points")):
                dpg.add_scatter_series(parent=self.tag+"_x_axis_scatter", x=x_vals, y=y_vals, tag=self.tag+"_hands_cloud_points")
            else:
                dpg.configure_item(self.tag+"_hands_cloud_points", x=x_vals, y=y_vals)
        else:
            if (dpg.does_item_exist(self.tag+"_hands_cloud_points")):
                dpg.configure_item(self.tag+"_hands_cloud_points", x=x_vals, y=y_vals)

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
