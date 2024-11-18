import source.nodes as main_nodes
import source.main_windows as mw_nodes
import source.environment_front_module as efm
import dearpygui.dearpygui as dpg
import threading

import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


class MainApp:
    def __init__(self):
        self.node_instances = {}
        self.links_instances = {}
        self.current_threads = {}
        self.current_textures_data = {}
        # Inicializar contexto de dearpygui
        dpg.create_context()
        with dpg.font_registry():
            #self.default_font = efm.dpg.add_font("./fonts/InconsolataNerdFont-Regular.ttf", 28)
            self.default_font = dpg.add_font("./fonts/Cantarell-Regular.ttf", 24)
        #efm.dpg.show_font_manager()
        dpg.bind_font(self.default_font)
        
        #crear venatana de aplicación
        dpg.create_viewport(title="Phoeni-vision", width=1280, height=720)
        with dpg.window(label="ventana principal", tag="main_window"):
            with dpg.menu_bar():
                with dpg.menu(label="Settings"):
                    dpg.add_menu_item(label="Entorno", callback=self.open_settings_modal)
                    dpg.add_menu_item(label="Salir", callback=dpg.stop_dearpygui)
        dpg.set_primary_window("main_window", True)

        with dpg.node_editor(parent="main_window", tag="main_node_editor", callback=self.link_callback, delink_callback=self.delink_callback):
            self.camera_node = mw_nodes.webcam_module.MainCameraFrameNode("main_node_editor")
            self.camera_node.prepare_webcam()
            self.current_textures_data["webcam_texture_data"] = self.camera_node.texture_data

        self.env_settings_modal = efm.ModalWindow(label="Configuración del entorno", fields=[""], buttons=[""], width=600, height=400)

        # Crear menú contextual como ventana flotante
        with dpg.window(label="Nodos", modal=True, show=False, tag="right_click_menu", pos=(0, 0), autosize=True):
            dpg.add_menu_item(label="Webcam output", callback=lambda: main_nodes.webcam_node.create_node(main_nodes.webcam_node.WebcamOutputNode, parent="main_node_editor", node_dictionary=self.node_instances))
            dpg.add_menu_item(label="Webcam input", callback=lambda: main_nodes.webcam_node.create_node(main_nodes.webcam_node.MediapipeInputOutputNode, parent="main_node_editor", node_dictionary=self.node_instances))

        # Crear un handler para detectar clic derecho
        with dpg.handler_registry():
            dpg.add_mouse_click_handler(callback=self.show_right_click_menu, button=-1)

    def show_right_click_menu(self, sender, app_data):
        # Mostrar el menú solo en el nodo de edición con clic derecho
        if app_data == dpg.mvMouseButton_Right:
            if (dpg.get_item_state("right_click_menu")['visible'] == True):
                return
            mouse_pos = dpg.get_mouse_pos()
            dpg.set_item_pos("right_click_menu", mouse_pos)
            dpg.show_item("right_click_menu")

    def link_callback(self, sender, app_data):
        #print(app_data)
        if (len(app_data) == 2):
            link = dpg.add_node_link(app_data[0], app_data[1], parent=sender)
        node_a_atag = dpg.get_item_alias(app_data[0])
        node_b_atag = dpg.get_item_alias(app_data[1])
        node_a_class_name = dpg.get_item_alias(dpg.get_item_parent(node_a_atag))
        node_b_class_name = dpg.get_item_alias(dpg.get_item_parent(node_b_atag))
        #alias_a = dpg.get_item_alias(dpg.get_item_children(node_a_tag, slot=1)[0])
        #alias_b = dpg.get_item_alias(dpg.get_item_children(node_b_tag, slot=1)[0])
        node_a_instance = self.node_instances.get(node_a_class_name, None)
        node_b_instance = self.node_instances.get(node_b_class_name, None)
        link_tag_name = node_a_atag+node_b_atag
        node_a_instance.connected_output_nodes[link_tag_name] = node_b_instance
        node_b_instance.connected_input_nodes[link_tag_name] = node_a_instance
        stop_event = threading.Event()
        self.current_threads[link] = [threading.Thread(target=node_a_instance.update_output_atts, args=(stop_event,)), stop_event]
        self.current_threads.get(link)[0].start()
        #threading.Thread(target=node_a_instance.update_output_atts).start()


        self.links_instances[link] = [
            [node_a_instance, node_a_atag],
            [node_b_instance, node_b_atag]
        ]

    def delink_callback(self, sender, app_data):
        dpg.delete_item(app_data)
        cur_thread = self.current_threads.get(app_data)
        link_data = self.links_instances.get(app_data)
        if (len(link_data[0][0].connected_output_nodes) <= 1):
            print("stoped_thread")
            cur_thread[1].set()
            cur_thread[0].join()
        #print(cur_thread)

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
    for cur_thread in app.current_threads:
        print(cur_thread)
