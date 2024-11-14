import source.main_windows as mw_nodes
import source.environment_front_module as efm
import dearpygui.dearpygui as dpg
import threading

class MainApp:
    def __init__(self):
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

        self.env_settings_modal = efm.ModalWindow(label="Configuración del entorno", fields=[""], buttons=[""], width=600, height=400)

        # Crear menú contextual como ventana flotante
        with dpg.window(label="Menú Contextual", modal=True, show=False, tag="right_click_menu", pos=(0, 0), autosize=True):
            dpg.add_menu_item(label="Entorno", callback=self.open_settings_modal)

        # Crear un handler para detectar clic derecho
        with dpg.handler_registry():
            dpg.add_mouse_click_handler(callback=self.show_right_click_menu, button=-1)

    def show_right_click_menu(self, sender, app_data):
        # Mostrar el menú solo en el nodo de edición con clic derecho
        if app_data == dpg.mvMouseButton_Right:
            mouse_pos = dpg.get_mouse_pos()
            dpg.set_item_pos("right_click_menu", mouse_pos)
            dpg.show_item("right_click_menu")
            if not (dpg.does_item_exist("test_node")):
                with dpg.node(label="Test node", tag="test_node", parent="main_node_editor"):
                    with dpg.node_attribute(label="input", attribute_type=dpg.mvNode_Attr_Input, tag="test_test"):
                        dpg.add_input_float(label="test", width=200, tag="test_input")
            print(dpg.get_mouse_pos())





    def link_callback(self, sender, app_data):
        if (len(app_data) == 2):
            dpg.add_node_link(app_data[0], app_data[1], parent=sender)
        node_a = dpg.get_item_alias(app_data[0])
        node_b = dpg.get_item_alias(app_data[1])
        alias_a = dpg.get_item_alias(dpg.get_item_children(node_a, slot=1)[0])
        alias_b = dpg.get_item_alias(dpg.get_item_children(node_b, slot=1)[0])
        #print(node_a)
        #print(node_b)
        #print(dpg.get_item_info(app_data[1]))
        print(alias_a)
        print(alias_b)
        

    def delink_callback(self, sender, app_data):
        dpg.delete_item(app_data)

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
