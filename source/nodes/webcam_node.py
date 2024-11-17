import dearpygui.dearpygui as dpg
#import numpy as np
from . import base_node as BN
import cv2 as cv
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
        while not(stop_thread.is_set()):
            #self.process_texture_data()
            #dpg.configure_item("image_input", texture_tag="webcam_texture")
            for node in self.connected_output_nodes:
                self.connected_output_nodes.get(node).update_input_atts()
            #print("node_a")
    


class MediapipeInputOutputNode(BN.BaseNode):
    def __init__(self, parent, tag):
        super().__init__(parent, tag)
        self.initial_texture_data = [0, 0, 0, 255] * (640 * 480)
        with dpg.texture_registry():
            self.initial_texture_id = dpg.add_raw_texture(640, 480, self.initial_texture_data, tag="mediapipe_texture")
        self.create_node()
        #prepare mediapipe configs
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.2, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

    def create_node(self):
        if (dpg.does_item_exist("mediapipe_out_in_node")):
            return
        with dpg.node(label="Mediapipa Out/In node", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="input_att", attribute_type=dpg.mvNode_Attr_Input, tag="moin_tag"):
                dpg.add_image(texture_tag=self.initial_texture_id, tag="image_input")

    def update_input_atts(self):
        #print("node_b")
        #dpg.configure_item("mediapipe_texture", default_value=dpg.get_item_user_data("webcam_texture"), format=dpg.mvFormat_Float_rgb)
        new_texture_data = self.process_texture_data()
        dpg.configure_item("mediapipe_texture", default_value=new_texture_data, format=dpg.mvFormat_Float_rgb)
        #dpg.set_value("mediapipe_texture", )
        #dpg.configure_item("image_input", texture_tag="mediapipe_texture")

    def process_texture_data(self):
        #prepare for mediapipe
        recovered_texture_data = dpg.get_item_user_data("webcam_texture")
        image = (recovered_texture_data * 255).astype(np.uint8)
        image = image.reshape((640, 480, 3))
        #print(image.shape)
        height, width, _ = image.shape
        frame_bgr = cv.cvtColor(image, cv.COLOR_RGB2BGR)

        #process with mediapip
        results = self.hands.process(image)
        #print(results)

        if (results.multi_hand_landmarks):
            print(results.multi_hand_landmarks)
            for landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(frame_bgr, landmarks, self.mp_hands.HAND_CONNECTIONS)
                #print("landmarks: ", landmarks)

        processed_bgr_to_rgb = cv.cvtColor(frame_bgr, cv.COLOR_BGR2RGB)
        processed_texture_data = processed_bgr_to_rgb.astype(np.float32) / 255.0


        return processed_texture_data


    def update_output_atts(self, stop_thread):
        while not(stop_thread.is_set()):
            pass

def create_node(node_class, parent, node_dictionary):
    tag = str(node_class.__name__)
    if (tag in node_dictionary):
        print("already exists")
        return

    node_dictionary[tag] = node_class(parent=parent, tag=tag)
