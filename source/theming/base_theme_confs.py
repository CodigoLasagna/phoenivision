import dearpygui.dearpygui as dpg

class Themer():
    def create_green_btn_theme():
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)  # Radio de redondeo
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 5)  # Padding interno
                dpg.add_theme_color(dpg.mvThemeCol_Button, [127, 218, 37])  # Color del botón
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [95, 199, 75])  # Color al pasar el mouse
                dpg.add_theme_color(dpg.mvThemeCol_Text, [0, 0, 0])
        return theme
    
    def create_color_window_theme():
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvChildWindow):
                #dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)
                #dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 10)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 10)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 10, 10)
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (65, 65, 65), category=dpg.mvThemeCat_Core)
        return theme
