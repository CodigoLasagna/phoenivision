import source.nodes as main_nodes
import source.main_windows as mw_nodes
import source.environment_front_module as efm
import dearpygui.dearpygui as dpg
import threading
import pandas as pd

import os

os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


class MainApp:
    def __init__(self):
        self.node_instances = {}
        self.links_instances = {}
        self.current_threads = {}
        self.current_textures_data = {}
        self.nodes_list_menu_items = {}
        self.nodes_ids = []
        self.window_size = [1920, 1080]
        # Inicializar contexto de dearpygui
        dpg.create_context()
        with dpg.font_registry():
            #self.default_font = efm.dpg.add_font("./fonts/InconsolataNerdFont-Regular.ttf", 28)
            self.default_font = dpg.add_font("./fonts/Cantarell-Regular.ttf", 24)
        #efm.dpg.show_font_manager()
        dpg.bind_font(self.default_font)
        
        #crear venatana de aplicación
        dpg.create_viewport(title="Phoeni-vision", width=self.window_size[0], height=self.window_size[1])
        with dpg.window(label="ventana principal", tag="main_window", autosize=True):
            with dpg.menu_bar():
                with dpg.menu(label="Settings"):
                    dpg.add_menu_item(label="Entorno", callback=self.open_settings_modal)
                    dpg.add_menu_item(label="Salir", callback=dpg.stop_dearpygui)
            with dpg.group(horizontal=True):
                with dpg.child_window(border=False, tag="main_window_left_panel"):
                    pass
                with dpg.child_window(border=False, tag="main_window_right_panel"):
                    with dpg.group():
                        with dpg.child_window(border=False, tag="top_right_panel"):
                            pass
                        with dpg.child_window(border=False, tag="bot_right_panel"):
                            pass
        dpg.set_primary_window("main_window", True)
        dpg.set_viewport_resize_callback(self.resize_callback)

        with dpg.node_editor(parent="main_window_left_panel", tag="main_node_editor", callback=self.link_callback, delink_callback=self.delink_callback, minimap=True, minimap_location=dpg.mvNodeMiniMap_Location_BottomRight):
            self.camera_node = mw_nodes.webcam_module.MainCameraFrameNode("main_node_editor")
            self.camera_node.prepare_webcam()
            self.current_textures_data["webcam_texture_data"] = self.camera_node.texture_data

        with dpg.child_window(parent="top_right_panel", tag="nodes_item_panel"):
            dpg.add_text("Panel de nodos")
            dpg.add_separator()
        with dpg.child_window(parent="bot_right_panel"):
            dpg.add_text("test")

        self.env_settings_modal = efm.ModalWindow(label="Configuración del entorno", fields=[""], buttons=[""], width=600, height=400)

            #dpg.add_menu_iem(label="Delete", callback=lambda: self.gen_node(main_nodes.webcam_node.WebcamOutputNode))
        with dpg.window(label="Nodos", modal=True, show=False, tag="right_click_menu", pos=(0, 0), autosize=True):
            dpg.add_menu_item(label="Webcam output node", callback=lambda: self.gen_node(main_nodes.webcam_node.WebcamOutputNode))
            with dpg.menu(label="Pattern recognition"):
                dpg.add_menu_item(label="Webcam hands i/o node", callback=lambda: self.gen_node(main_nodes.webcam_node.MediapipeInputHandsOutputNode))
                with dpg.menu(label="face recognition"):
                    dpg.add_menu_item(label="Webcam face i/o node", callback=lambda: self.gen_node(main_nodes.webcam_node.MediapipeInputFaceOutputNode))
                    dpg.add_menu_item(label="Webcam face b i/o node", callback=lambda: self.gen_node(main_nodes.webcam_node.MediapipeInputFaceBOutputNode))
                dpg.add_menu_item(label="Webcam pose i/o node", callback=lambda: self.gen_node(main_nodes.webcam_node.MediapipeInputPoseOutputNode))
                dpg.add_menu_item(label="Webcam object i/o node", callback=lambda: self.gen_node(main_nodes.webcam_node.MediapipeInputObjectOutputNode))
            with dpg.menu(label="Data Processing"):
                dpg.add_menu_item(label="DataColectorNode", callback=lambda: self.gen_node(main_nodes.processing_nodes.StaticDatabaseManagerNode))
                dpg.add_menu_item(label="MultiGraphCapNode", callback=lambda: self.gen_node(main_nodes.processing_nodes.MultiGraphCapNode))
            with dpg.menu(label="Modeling"):
                dpg.add_menu_item(label="StaticModelMaker", callback=lambda: self.gen_node(main_nodes.algorithm_nodes.StaticModelMaker))

        # Crear un handler para detectar clic derecho
        with dpg.handler_registry():
            dpg.add_mouse_click_handler(callback=self.show_right_click_menu, button=-1)
    def gen_node(self, node_class):
        main_nodes.webcam_node.create_node(node_class, parent="main_node_editor", node_dictionary=self.node_instances, nodes_ids=self.nodes_ids)
        #print(self.node_instances)
        for name, node in self.node_instances.items():
            if (node.tag in self.nodes_list_menu_items):
                continue
            self.nodes_list_menu_items[node.tag] = [
                    dpg.add_combo(parent="nodes_item_panel", width=int(dpg.get_item_rect_size("top_right_panel")[0] - 16),
                        default_value=node.tag+"_options",
                        items=["Eliminar"],
                        callback=lambda sender: self.node_combo_item(node.tag, dpg.get_value(sender)),
                        tag=node.tag+"_options"
                    ),
                    node
                ]


    def resize_callback(self):
        viewport_width = dpg.get_viewport_width()
        viewport_height = dpg.get_viewport_height()
        dpg.set_item_width("main_window_left_panel", int(viewport_width * 0.7))
        dpg.set_item_width("main_window_right_panel", int(viewport_width * 0.3) - 20)
        dpg.set_item_height("top_right_panel", int(viewport_height * 0.3))
        dpg.set_item_height("bot_right_panel", int(viewport_height * 0.7) - 50)

        for name, node in self.nodes_list_menu_items.items():
            dpg.set_item_width(node[0], int(dpg.get_item_rect_size("top_right_panel")[0] - 16))

    def show_right_click_menu(self, sender, app_data):
        # Mostrar el menú solo en el nodo de edición con clic derecho
        if app_data == dpg.mvMouseButton_Right:
            # Obtener las coordenadas del mouse
            mouse_pos = dpg.get_mouse_pos(local=False)
            
            # Obtener las coordenadas y el tamaño del node_editor
            editor_rect = dpg.get_item_rect_size("main_window_left_panel")  # Coordenadas del node_editor
    
            # Verificar si el clic ocurrió dentro del área del node_editor
            if 0 <= mouse_pos[0] <= editor_rect[0] and 0 <= mouse_pos[1] <= editor_rect[1]:
                self.spawn_nodes_menu()

    def spawn_nodes_menu(self):
        mouse_pos = dpg.get_mouse_pos(local=False)
        if dpg.get_item_state("right_click_menu")['visible'] == True:
            return
        # Establecer la posición del menú contextual donde ocurrió el clic
        dpg.set_item_pos("right_click_menu", mouse_pos)
        # Mostrar el menú contextual
        dpg.show_item("right_click_menu")

    def link_callback(self, sender, app_data):
        #print(app_data)
        node_a_atag = dpg.get_item_alias(app_data[0])
        node_b_atag = dpg.get_item_alias(app_data[1])
        node_a_class_name = dpg.get_item_alias(dpg.get_item_parent(node_a_atag))
        node_b_class_name = dpg.get_item_alias(dpg.get_item_parent(node_b_atag))
        node_a_instance = self.node_instances.get(node_a_class_name, None)
        node_b_instance = self.node_instances.get(node_b_class_name, None)
        #if (node_a_instance.node_type)
        if (not self.check_compatible_node_types(node_a_instance, node_b_instance)):
            return
        if (len(app_data) == 2):
            link = dpg.add_node_link(app_data[0], app_data[1], parent=sender)
        #alias_a = dpg.get_item_alias(dpg.get_item_children(node_a_tag, slot=1)[0])
        #alias_b = dpg.get_item_alias(dpg.get_item_children(node_b_tag, slot=1)[0])
        link_tag_name = node_a_atag+node_b_atag
        node_a_instance.connected_output_nodes[link_tag_name] = node_b_instance
        node_b_instance.connected_input_nodes[link_tag_name] = node_a_instance
        stop_event = threading.Event()
        self.current_threads[link] = [threading.Thread(target=node_a_instance.update_output_atts, args=(stop_event,)), stop_event]
        self.current_threads.get(link)[0].start()
        #print(self.current_threads[link])
        #threading.Thread(target=node_a_instance.update_output_atts).start()


        self.links_instances[link] = [
            [node_a_instance, link_tag_name], #NOTE: setup link_tag_name
            [node_b_instance, link_tag_name]  #NOTE: setup link_tag_name
        ]
    def check_compatible_node_types(self, node_a, node_b):
        enums = main_nodes.base_node.NodeType
        valid_combinations = [
            (enums.WEBCAM_BASE_NODE, enums.PATTER_REC_NODE),
            (enums.PATTER_REC_NODE, enums.WEBCAM_BASE_NODE),
            (enums.PATTER_REC_NODE, enums.DATA_PROC_NODE),
            (enums.DATA_PROC_NODE, enums.PATTER_REC_NODE),
            (enums.DATA_PROC_NODE, enums.MODEL_LAYER_NODE),
            (enums.MODEL_LAYER_NODE, enums.DATA_PROC_NODE),
            (enums.PATTER_REC_NODE, enums.MODEL_LAYER_NODE),
        ]
        return  (node_a.node_type, node_b.node_type) in valid_combinations
    
    def delete_node(self, node_tag):
        node_instance = self.node_instances.get(node_tag)
        if not node_instance:
            return

        for link_tag, connected_node in list(node_instance.connected_output_nodes.items()):
            link_item = next(
                    (key for key, value in self.links_instances.items() if value[0][1] == link_tag)
                    , None
            )
            if link_item:
                self.delink_callback("main_node_editor", link_item)

        for link_tag, connected_node in list(node_instance.connected_input_nodes.items()):
            link_item = next(
                (key for key, value in self.links_instances.items() if value[1][1] == link_tag),
                None
            )
            if link_item:
                self.delink_callback("main_node_editor", link_item)

        dpg.delete_item(node_instance.tag)
        self.node_instances.pop(node_tag, None)
        node_instance.clear_self()
        menu_item = self.nodes_list_menu_items.pop(node_tag, None)
        if (menu_item):
            dpg.delete_item(menu_item[0])
    def node_combo_item(self, node, selected_option):
        dpg.configure_item(node+"_options", default_value=node+"_options")
        if (selected_option == "Eliminar"):
            self.delete_node(node)



    def delink_callback(self, sender, app_data):
        dpg.delete_item(app_data)
        cur_thread = self.current_threads.get(app_data)
        link_data = self.links_instances.get(app_data)
        #print(len(link_data[0][0].connected_output_nodes))
        if (len(link_data[0][0].connected_output_nodes) <= 1):
            #print("stoped_thread")
            cur_thread[1].set()
            cur_thread[0].join()
            self.current_threads.pop(app_data)

        link_data[0][0].connected_output_nodes.pop(link_data[0][1], None)
        link_data[1][0].connected_input_nodes.pop(link_data[1][1], None)


        del self.links_instances[app_data]

    def open_settings_modal(self):
        self.env_settings_modal.show_popup()

    def run(self):
        # Configuración y ejecución de Dear PyGui
        dpg.create_viewport() 
        dpg.setup_dearpygui()
        dpg.show_viewport()
        #self.camera_node.camera_loop()
        dpg.set_frame_callback(callback=threading.Thread(target=self.camera_node.camera_loop).start, frame=1)
        dpg.start_dearpygui()
        dpg.destroy_context()

# Crear una instancia de la aplicación y ejecutarla
if __name__ == "__main__":
    app = MainApp()
    app.run()
    #for cur_thread in app.current_threads:
    #    print(cur_thread)
