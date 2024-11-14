import dearpygui.dearpygui as dpg
import cv2 as cv
import numpy as np

class MainCameraFrameNode:
    def __init__(self, parent):
        self.parent = parent
        self.width = 320
        self.height = 240
        self.fps = 60
        self.on_update = False

        with dpg.window(label="Opciones de la cámara"):
            dpg.add_button(label="set 320x240", callback=self.make_240)
            dpg.add_button(label="set 640x480", callback=self.make_480)
            dpg.add_button(label="set 1280x70", callback=self.make_720)

    def make_240(self):
        self.width = 320
        self.height = 240
        self.on_update = True
    def make_480(self):
        self.width = 640
        self.height = 480
        self.on_update = True
    def make_720(self):
        self.width = 1280
        self.height = 720
        self.on_update = True

    def prepare_webcam(self):
        self.cap = cv.VideoCapture(0)
        self.configure_camera()
        self.ret, self.frame = self.cap.read()

        self.update_texture()


    def configure_camera(self):
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv.CAP_PROP_FPS, self.fps)

    def update_texture(self):
        # Procesar la imagen de la cámara
        self.data = np.flip(self.frame, 2)  # Convertir de BGR a RGB
        self.data = self.data.ravel()  # Aplanar la imagen
        self.data = np.asfarray(self.data, dtype='f')  # Asegurarse de que sea un array de tipo float
        self.texture_data = np.true_divide(self.data, 255.0)  # Normalizar entre 0 y 1

        # Verificar si la textura ya existe y eliminarla si es necesario
        if dpg.does_item_exist("texture_tag"):
            dpg.delete_item("texture_tag")
            dpg.remove_alias("texture_tag")

        # Crear una nueva textura con los valores actuales de width y height
        with dpg.texture_registry(show=False):
            dpg.add_raw_texture(self.width, self.height, self.texture_data, tag="texture_tag", format=dpg.mvFormat_Float_rgb)

        # Mostrar la nueva textura en la ventana
        if dpg.does_item_exist("image_cam"):
            dpg.configure_item(item="image_cam", texture_tag="texture_tag", width=self.width, height=self.height)
            dpg.configure_item(item="image_input", texture_tag="texture_tag", width=self.width, height=self.height)
            #dpg.configure_item(item="webcam_node", width=self.width, height=self.height)
        else:
            #with dpg.window(label="webcam_menu", tag="webcam_menu"):
            #    dpg.add_image(texture_tag="texture_tag", tag="image_cam")
            with dpg.node(label="Webcam node input", tag="mediapipe_node"):
                with dpg.node_attribute(label="Webcam input", attribute_type=dpg.mvNode_Attr_Input):
                    dpg.add_image(texture_tag="texture_tag", tag="image_input")

            with dpg.node(label="Webcam node output", tag="webcam_node"):
                with dpg.node_attribute(label="Webcam output", attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_image(texture_tag="texture_tag", tag="image_cam")
                #with dpg.node_attribute(label="Webcam node", tag="webcam_node", attribute_type=dpg.mvNode_Attr_Static):
                #    dpg.add_image(texture_tag="texture_tag", tag="image_cam")

    def camera_loop(self):
        while dpg.is_dearpygui_running():
            if not self.cap.isOpened():
                continue
            self.ret, self.frame = self.cap.read()
            if not self.ret:
                continue

            self.data = np.flip(self.frame, 2)
            self.data = self.data.ravel()
            self.data = np.asfarray(self.data, dtype='f')
            self.texture_data = np.true_divide(self.data, 255.0)

            if (self.on_update):
                self.configure_camera()
                self.ret, self.frame = self.cap.read()
                self.update_texture()
                self.on_update = False

            if (dpg.does_item_exist("texture_tag")):
                dpg.set_value("texture_tag", self.texture_data)
            else:
                self.update_texture()

