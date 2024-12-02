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

    def create_yellow_btn_theme():
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)  # Radio de redondeo
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 5)  # Padding interno
                dpg.add_theme_color(dpg.mvThemeCol_Button, [236, 178, 46])  # Color del botón
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [211, 157, 32])  # Color al pasar el mouse
                dpg.add_theme_color(dpg.mvThemeCol_Text, [0, 0, 0])
        return theme
    
    def create_color_window_theme():
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 10)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 10, 10)
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (65, 65, 65), category=dpg.mvThemeCat_Core)
        return theme

    def create_contour_color_text(outline_col = [77, 155, 230]):
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)  # Radio de redondeo
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 5)  # Padding interno
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 2)
                dpg.add_theme_color(dpg.mvThemeCol_Border, outline_col)
                dpg.add_theme_color(dpg.mvThemeCol_Button, [70, 70, 70])  # Color del botón
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [70, 70, 70])  # Color al pasar el mouse
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [70, 70, 70])  # Color al pasar el mouse
                dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 255, 255])
        return theme