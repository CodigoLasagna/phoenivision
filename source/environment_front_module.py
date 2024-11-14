import dearpygui.dearpygui as dpg

class ModalWindow:
    def __init__(self,label, fields, buttons, width, height):
        self.width = width
        self.height = height
        self.label = label
        self.fields = fields
        self.buttons = buttons

    def show_popup(self):
        with dpg.window(modal=True, label=self.label, width=self.width, height=self.height):
            dpg.add_text("hola mundo")

