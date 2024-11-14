import source.main_windows as mw_nodes
import source.environment_front_module as efm
import dearpygui.dearpygui as dpg

class MainApp:
    def __init__(self):
        # Inicializar contexto de dearpygui
        dpg.create_context()
        with dpg.font_registry():
            #self.default_font = efm.dpg.add_font("./fonts/InconsolataNerdFont-Regular.ttf", 28)
            self.default_font = dpg.add_font("./fonts/Cantarell-Regular.ttf", 21)
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


    def link_callback(self, sender, app_data):
        if (len(app_data) == 2):
            dpg.add_node_link(app_data[0], app_data[1], parent=sender)

    def delink_callback(self, sender, app_data):
        dpg.delete_item(app_data)

    def open_settings_modal(self):
        self.env_settings_modal.show_popup()

    def run(self):
        # Configuración y ejecución de Dear PyGui
        dpg.create_viewport() 
        dpg.setup_dearpygui()
        dpg.show_viewport()
        self.camera_node.camera_loop()
        dpg.start_dearpygui()
        dpg.destroy_context()

# Crear una instancia de la aplicación y ejecutarla
if __name__ == "__main__":
    app = MainApp()
    app.run()