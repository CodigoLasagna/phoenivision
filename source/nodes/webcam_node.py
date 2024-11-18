import dearpygui.dearpygui as dpg
#import numpy as np
from . import base_node as BN
#import cv2 as cv
import mediapipe as mp
import numpy as np

class WebcamOutputNode(BN.BaseNode):
    def __init__(self, parent, tag):
        super().__init__(parent, tag)
        self.create_node()

    def create_node(self):
        if (dpg.does_item_exist("webcam_output_node")):
            return
        with dpg.node(label="Webcam output node", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="output_att", attribute_type=dpg.mvNode_Attr_Output, tag="won_tag"):
                dpg.add_image(texture_tag="webcam_texture", tag="image_output")

    def update_output_atts(self, stop_thread):
        if (self.update_loop == True):
            return
        self.update_loop = True
        while not(stop_thread.is_set()):
            #self.process_texture_data()
            #dpg.configure_item("image_input", texture_tag="webcam_texture")
            if not(self.lock):
                break
            for link_tag_name, node_instance in list(self.connected_output_nodes.items()):
                #self.connected_output_nodes.get(node).update_input_atts()
                node_instance.update_input_atts()
            #print("node_a")
        self.update_loop = False
    


class MediapipeInputHandsOutputNode(BN.BaseNode):
    def __init__(self, parent, tag):
        super().__init__(parent, tag)
        self.initial_texture_data = [0, 0, 0, 255] * (320 * 240)
        with dpg.texture_registry():
            self.initial_texture_id = dpg.add_raw_texture(320, 240, self.initial_texture_data, tag="mediapipe_hands_texture")
        self.create_node()
        #prepare mediapipe configs
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
        self.mp_drawing = mp.solutions.drawing_utils


    def create_node(self):
        if (dpg.does_item_exist(self.tag)):
            return
        with dpg.node(label="Mediapipe Hands Out/In node", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="input_att", attribute_type=dpg.mvNode_Attr_Input, tag="mihon_tag"):
                dpg.add_image(texture_tag=self.initial_texture_id, tag="himage_input")

    def update_input_atts(self):
        #print("node_b")
        #dpg.configure_item("mediapipe_texture", default_value=dpg.get_item_user_data("webcam_texture"), format=dpg.mvFormat_Float_rgb)
        new_texture_data = self.process_texture_data()
        dpg.configure_item("mediapipe_hands_texture", default_value=new_texture_data, format=dpg.mvFormat_Float_rgb)
        #dpg.set_value("mediapipe_texture", )
        #dpg.configure_item("image_input", texture_tag="mediapipe_texture")

    def process_texture_data(self):
        #prepare for mediapipe
        recovered_texture_data = dpg.get_item_user_data("webcam_texture")
        image = (recovered_texture_data * 255.0).astype(np.uint8)
        image = image.reshape((240, 320, 3))
        frame_rgb = image

        #process with mediapip
        results = self.hands.process(frame_rgb)
        #print(results)

        if (results.multi_hand_landmarks):
            #print(results.multi_hand_landmarks)
            for landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(frame_rgb, landmarks, self.mp_hands.HAND_CONNECTIONS)
                #print("landmarks: ", landmarks)

        processed_bgr_to_rgb = frame_rgb
        processed_texture_data = processed_bgr_to_rgb.astype(np.float32) / 255.0


        return processed_texture_data


    def update_output_atts(self, stop_thread):
        if (self.update_loop == True):
            return
        self.update_loop = True
        while not(stop_thread.is_set()):
            pass
        self.update_loop = False

class MediapipeInputFaceOutputNode(BN.BaseNode):
    def __init__(self, parent, tag):
        super().__init__(parent, tag)
        self.initial_texture_data = [0, 0, 0, 255] * (320 * 240)
        with dpg.texture_registry():
            self.initial_texture_id = dpg.add_raw_texture(320, 240, self.initial_texture_data, tag="mediapipe_face_texture")
        self.create_node()
        #prepare mediapipe configs
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.mp_drawing = mp.solutions.drawing_utils



    def create_node(self):
        if (dpg.does_item_exist(self.tag)):
            return
        with dpg.node(label="Mediapipe Face Out/In node", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="input_att", attribute_type=dpg.mvNode_Attr_Input, tag="mifon_tag"):
                dpg.add_image(texture_tag=self.initial_texture_id, tag="fimage_input")

    def update_input_atts(self):
        new_texture_data = self.process_texture_data()
        dpg.configure_item("mediapipe_face_texture", default_value=new_texture_data, format=dpg.mvFormat_Float_rgb)

    def process_texture_data(self):
        #prepare for mediapipe
        recovered_texture_data = dpg.get_item_user_data("webcam_texture")
        image = (recovered_texture_data * 255.0).astype(np.uint8)
        image = image.reshape((240, 320, 3))
        frame_rgb = image

        #process with mediapip
        results = self.face_mesh.process(frame_rgb)
        #print(results)

        if (results.multi_face_landmarks):
            for face_landmarks in results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    image=frame_rgb,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                )

        processed_bgr_to_rgb = frame_rgb
        processed_texture_data = processed_bgr_to_rgb.astype(np.float32) / 255.0


        return processed_texture_data


    def update_output_atts(self, stop_thread):
        if (self.update_loop == True):
            return
        self.update_loop = True
        while not(stop_thread.is_set()):
            while self.lock:
                for link_tag_name, node_instance in list(self.connected_output_nodes.items()):
                    #self.connected_output_nodes.get(node).update_input_atts()
                    node_instance.update_input_atts()
        self.update_loop = False

def create_node(node_class, parent, node_dictionary):
    tag = str(node_class.__name__)
    if (tag in node_dictionary):
        print("already exists")
        return

    node_dictionary[tag] = node_class(parent=parent, tag=tag)
