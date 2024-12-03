import dearpygui.dearpygui as dpg
#import numpy as np
from . import base_node as BN
#import cv2 as cv
import mediapipe as mp
import numpy as np
import random

class WebcamOutputNode(BN.BaseNode):
    def __init__(self, parent, tag, unique_id):
        super().__init__(parent, tag, unique_id)
        self.create_node()
        mouse_pos = dpg.get_mouse_pos(local=False)
        mouse_pos[0] = mouse_pos[0] - 180
        mouse_pos[1] = mouse_pos[1] - 120
        dpg.set_item_pos(self.tag, mouse_pos)
        self.node_type = BN.NodeType.WEBCAM_BASE_NODE
        self.children_tags.append(self.tag+"_out_tag")
        self.children_tags.append("image_output")

    def create_node(self):
        if (dpg.does_item_exist(self.tag)):
            return
        with dpg.node(label="webcam_output_node", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="output_att", attribute_type=dpg.mvNode_Attr_Output, tag=self.tag+"_out_tag"):
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
            #self.node_output_data = dpg.get_item_user_data("webcam_texture")
            #dpg.set_item_user_data("won_tag", dpg.get_item_user_data("webcam_texture"))
            for link_tag_name, node_instance in list(self.connected_output_nodes.items()):
                node_instance.update_input_atts()
                #print('webcam')
            #print("node_a")
        self.update_loop = False


class MediapipeInputHandsOutputNode(BN.BaseNode):
    def __init__(self, parent, tag, unique_id):
        super().__init__(parent, tag, unique_id)
        self.node_type = BN.NodeType.PATTER_REC_NODE
        self.initial_texture_data = [0, 0, 0, 255] * (320 * 240)
        with dpg.texture_registry():
            self.initial_texture_id = dpg.add_raw_texture(320, 240, self.initial_texture_data, tag=self.tag+"tex")
        self.create_node()
        #prepare mediapipe configs
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.8, min_tracking_confidence=0.8)
        self.mp_drawing = mp.solutions.drawing_utils
        mouse_pos = dpg.get_mouse_pos(local=False)
        mouse_pos[0] = mouse_pos[0] - 180
        mouse_pos[1] = mouse_pos[1] - 120
        dpg.set_item_pos(self.tag, mouse_pos)
        self.children_tags.append(self.tag+"tex")
        self.children_tags.append(self.tag+"_in_tag")
        self.children_tags.append(self.tag+"_out_tag")


    def create_node(self):
        if (dpg.does_item_exist(self.tag)):
            return
        with dpg.node(label="Mediapipe Hands Out/In node", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="input_att", attribute_type=dpg.mvNode_Attr_Input, tag=self.tag+"_in_tag"):
                dpg.add_image(texture_tag=self.initial_texture_id)
            with dpg.node_attribute(label="output_att", attribute_type=dpg.mvNode_Attr_Output, tag=self.tag+"_out_tag"):
                dpg.add_text("Data output")


    def update_input_atts(self):
        #print("node_b")
        #dpg.configure_item("mediapipe_texture", default_value=dpg.get_item_user_data("webcam_texture"), format=dpg.mvFormat_Float_rgb)
        new_texture_data = self.process_texture_data()
        if dpg.does_item_exist(self.tag+"tex"):
            dpg.configure_item(self.tag+"tex", default_value=new_texture_data, format=dpg.mvFormat_Float_rgb)
        #dpg.set_value("mediapipe_texture", )
        #dpg.configure_item("image_input", texture_tag="mediapipe_texture")

    def process_texture_data(self):
        #prepare for mediapipe
        #recovered_texture_data = dpg.get_item_user_data("won_tag")
        recovered_texture_data = dpg.get_item_user_data("webcam_texture")
        #recovered_texture_data = self.connected_input_nodes.items()[0].data_output
        #print(dpg.get_item_user_data("won_tag"))
        image = (recovered_texture_data * 255.0).astype(np.uint8)
        image = image.reshape((240, 320, 3))
        frame_rgb = image

        #process with mediapip
        results = self.hands.process(frame_rgb)

        #keypoints_combined = {}
        #if (results.multi_hand_landmarks):
        #    for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
        #        hand_type = handedness.classification[0].label
        #        keypoints = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
        #        keypoints_combined[hand_type] = keypoints
        #        self.mp_drawing.draw_landmarks(frame_rgb, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        keypoints_combined = []
        #dummy_value = (float('nan'), float('nan'), float('nan'))
        if results.multi_hand_landmarks:
            if len(results.multi_hand_landmarks) == 2:
                # Se detectan ambas manos, agregamos los puntos de ambas
                keypoints_left = [(lm.x, lm.y, lm.z) for lm in results.multi_hand_landmarks[0].landmark]  # Mano izquierda
                keypoints_right = [(lm.x, lm.y, lm.z) for lm in results.multi_hand_landmarks[1].landmark]  # Mano derecha
                keypoints_combined.extend([keypoints_right, keypoints_left])
        
            elif len(results.multi_hand_landmarks) == 1:
                # Si solo se detecta una mano, la colocamos en el lugar correcto
                hand_landmarks = results.multi_hand_landmarks[0].landmark
                keypoints = [(lm.x, lm.y, lm.z) for lm in hand_landmarks]
                
                #la imagen esta volteada
                if "Left" in results.multi_handedness[0].classification[0].label:  # Si es mano izquierda
                    #keypoints_combined.extend([[dummy_value] * 21, keypoints])  # Agregamos la mano izquierda
                    keypoints_combined.extend([[] , keypoints])  # Agregamos la mano izquierda
                else:  # Si es mano derecha
                    #keypoints_combined.extend([keypoints, [dummy_value] * 21])  # Agregamos la mano izquierda
                    keypoints_combined.extend([keypoints, []])  # Agregamos la mano izquierda

            for landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(frame_rgb, landmarks, self.mp_hands.HAND_CONNECTIONS)
        else:
            #keypoints_combined.extend([[dummy_value] * 21, [dummy_value] * 21])
            keypoints_combined.extend([[], []])

        processed_bgr_to_rgb = frame_rgb
        processed_texture_data = processed_bgr_to_rgb.astype(np.float32) / 255.0

        self.node_output_data = [0, keypoints_combined]
        #print("--------")
        #print(keypoints_combined)
        #print(keypoints_combined[0])
        #print(keypoints_combined)


        return processed_texture_data


    def update_output_atts(self, stop_thread):
        if (self.update_loop == True):
            return
        self.update_loop = True
        while not(stop_thread.is_set()):
            #pass
            if not(self.lock):
                break
            for link_tag_name, node_instance in list(self.connected_output_nodes.items()):
                node_instance.update_input_atts()
                #print('hands')
        self.update_loop = False

class MediapipeInputFaceOutputNode(BN.BaseNode):
    def __init__(self, parent, tag, unique_id):
        super().__init__(parent, tag, unique_id)
        self.node_type = BN.NodeType.PATTER_REC_NODE
        self.initial_texture_data = [0, 0, 0, 255] * (320 * 240)
        with dpg.texture_registry():
            self.initial_texture_id = dpg.add_raw_texture(320, 240, self.initial_texture_data, tag=self.tag+"tex")
        self.create_node()
        #prepare mediapipe configs
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.mp_drawing = mp.solutions.drawing_utils
        mouse_pos = dpg.get_mouse_pos(local=False)
        mouse_pos[0] = mouse_pos[0] - 180
        mouse_pos[1] = mouse_pos[1] - 120
        dpg.set_item_pos(self.tag, mouse_pos)
        self.children_tags.append(self.tag+"tex")
        self.children_tags.append(self.tag+"_in_tag")
        self.children_tags.append(self.tag+"_out_tag")

    def create_node(self):
        if (dpg.does_item_exist(self.tag)):
            return
        with dpg.node(label="Mediapipe Face Out/In node", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="input_att", attribute_type=dpg.mvNode_Attr_Input, tag=self.tag+"_in_tag"):
                dpg.add_image(texture_tag=self.initial_texture_id)
            with dpg.node_attribute(label="output_att", attribute_type=dpg.mvNode_Attr_Output, tag=self.tag+"_out_tag"):
                dpg.add_text("Data output")

    def update_input_atts(self):
        new_texture_data = self.process_texture_data()
        if dpg.does_item_exist(self.tag+"tex"):
            dpg.configure_item(self.tag+"tex", default_value=new_texture_data, format=dpg.mvFormat_Float_rgb)

    def process_texture_data(self):
        #prepare for mediapipe
        recovered_texture_data = dpg.get_item_user_data("webcam_texture")
        image = (recovered_texture_data * 255.0).astype(np.uint8)
        image = image.reshape((240, 320, 3))
        frame_rgb = image

        #process with mediapip
        results = self.face_mesh.process(frame_rgb)

        if (results.multi_face_landmarks):
            for face_landmarks in results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(frame_rgb, face_landmarks, self.mp_face_mesh.FACEMESH_TESSELATION)

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

class MediapipeInputPoseOutputNode(BN.BaseNode):
    def __init__(self, parent, tag, unique_id):
        super().__init__(parent, tag, unique_id)
        self.node_type = BN.NodeType.PATTER_REC_NODE
        self.initial_texture_data = [0, 0, 0, 255] * (320 * 240)
        with dpg.texture_registry():
            self.initial_texture_id = dpg.add_raw_texture(320, 240, self.initial_texture_data, tag=self.tag+"tex")
        self.create_node()
        #prepare mediapipe configs
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.mp_drawing = mp.solutions.drawing_utils
        mouse_pos = dpg.get_mouse_pos(local=False)
        mouse_pos[0] = mouse_pos[0] - 180
        mouse_pos[1] = mouse_pos[1] - 120
        dpg.set_item_pos(self.tag, mouse_pos)
        self.children_tags.append(self.tag+"tex")
        self.children_tags.append(self.tag+"_in_tag")
        self.children_tags.append(self.tag+"_out_tag")

    def create_node(self):
        if (dpg.does_item_exist(self.tag)):
            return
        with dpg.node(label="Mediapipe Pose Out/In node", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="input_att", attribute_type=dpg.mvNode_Attr_Input, tag=self.tag+"_in_tag"):
                dpg.add_image(texture_tag=self.initial_texture_id)
            with dpg.node_attribute(label="output_att", attribute_type=dpg.mvNode_Attr_Output, tag=self.tag+"_out_tag"):
                dpg.add_text("Data output")

    def update_input_atts(self):
        new_texture_data = self.process_texture_data()
        if dpg.does_item_exist(self.tag+"tex"):
            dpg.configure_item(self.tag+"tex", default_value=new_texture_data, format=dpg.mvFormat_Float_rgb)

    def process_texture_data(self):
        #prepare for mediapipe
        recovered_texture_data = dpg.get_item_user_data("webcam_texture")
        image = (recovered_texture_data * 255.0).astype(np.uint8)
        image = image.reshape((240, 320, 3))
        frame_rgb = image

        #process with mediapip
        results = self.pose.process(frame_rgb)

        save_keypoints = []
        if (results.pose_landmarks):
            self.mp_drawing.draw_landmarks(frame_rgb, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            save_keypoints = [(lm.x, lm.y, lm.z) for lm in results.pose_landmarks.landmark]
            #for landmakrs in results.pose_landmarks:
            #    keypoints = [(lm.x, lm.y, lm.z) for lm in landmakrs]

        processed_bgr_to_rgb = frame_rgb
        processed_texture_data = processed_bgr_to_rgb.astype(np.float32) / 255.0

        #print(save_keypoints)
        #print(len(save_keypoints))
        self.node_output_data = [1, [save_keypoints]]


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

class MediapipeInputFaceBOutputNode(BN.BaseNode):
    def __init__(self, parent, tag, unique_id):
        super().__init__(parent, tag, unique_id)
        self.node_type = BN.NodeType.PATTER_REC_NODE
        self.initial_texture_data = [0, 0, 0, 255] * (320 * 240)
        with dpg.texture_registry():
            self.initial_texture_id = dpg.add_raw_texture(320, 240, self.initial_texture_data, tag=self.tag+"tex")
        self.create_node()
        #prepare mediapipe configs
        self.mp_face_det = mp.solutions.face_detection
        self.face_det = self.mp_face_det.FaceDetection(min_detection_confidence=0.7)
        self.mp_drawing = mp.solutions.drawing_utils
        mouse_pos = dpg.get_mouse_pos(local=False)
        mouse_pos[0] = mouse_pos[0] - 180
        mouse_pos[1] = mouse_pos[1] - 120
        dpg.set_item_pos(self.tag, mouse_pos)
        self.children_tags.append(self.tag+"tex")
        self.children_tags.append(self.tag+"_in_tag")
        self.children_tags.append(self.tag+"_out_tag")

    def create_node(self):
        if (dpg.does_item_exist(self.tag)):
            return
        with dpg.node(label="Mediapipe Face Basic Out/In node", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="input_att", attribute_type=dpg.mvNode_Attr_Input, tag=self.tag+"_in_tag"):
                dpg.add_image(texture_tag=self.initial_texture_id)
            with dpg.node_attribute(label="output_att", attribute_type=dpg.mvNode_Attr_Output, tag=self.tag+"_out_tag"):
                dpg.add_text("Data output")

    def update_input_atts(self):
        new_texture_data = self.process_texture_data()
        if dpg.does_item_exist(self.tag+"tex"):
            dpg.configure_item(self.tag+"tex", default_value=new_texture_data, format=dpg.mvFormat_Float_rgb)

    def process_texture_data(self):
        #prepare for mediapipe
        recovered_texture_data = dpg.get_item_user_data("webcam_texture")
        image = (recovered_texture_data * 255.0).astype(np.uint8)
        image = image.reshape((240, 320, 3))
        frame_rgb = image

        #process with mediapip
        results = self.face_det.process(frame_rgb)

        if (results.detections):
            for detection in results.detections:
                self.mp_drawing.draw_detection(frame_rgb, detection)

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

class MediapipeInputObjectOutputNode(BN.BaseNode):
    def __init__(self, parent, tag, unique_id):
        super().__init__(parent, tag, unique_id)
        self.node_type = BN.NodeType.PATTER_REC_NODE
        self.initial_texture_data = [0, 0, 0, 255] * (320 * 240)
        with dpg.texture_registry():
            self.initial_texture_id = dpg.add_raw_texture(320, 240, self.initial_texture_data, tag=self.tag+"tex")
        self.create_node()
        #prepare mediapipe configs
        self.mp_objectron = mp.solutions.objectron
        self.objectron = self.mp_objectron.Objectron(static_image_mode=False, max_num_objects=5, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        mouse_pos = dpg.get_mouse_pos(local=False)
        mouse_pos[0] = mouse_pos[0] - 180
        mouse_pos[1] = mouse_pos[1] - 120
        dpg.set_item_pos(self.tag, mouse_pos)
        self.children_tags.append(self.tag+"tex")
        self.children_tags.append(self.tag+"_in_tag")
        self.children_tags.append(self.tag+"_out_tag")

    def create_node(self):
        if (dpg.does_item_exist(self.tag)):
            return
        with dpg.node(label="Mediapipe Object Out/In node", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="input_att", attribute_type=dpg.mvNode_Attr_Input, tag=self.tag+"_in_tag"):
                dpg.add_image(texture_tag=self.initial_texture_id)
            with dpg.node_attribute(label="output_att", attribute_type=dpg.mvNode_Attr_Output, tag=self.tag+"_out_tag"):
                dpg.add_text("Data output")

    def update_input_atts(self):
        new_texture_data = self.process_texture_data()
        if dpg.does_item_exist(self.tag+"tex"):
            dpg.configure_item(self.tag+"tex", default_value=new_texture_data, format=dpg.mvFormat_Float_rgb)

    def process_texture_data(self):
        #prepare for mediapipe
        recovered_texture_data = dpg.get_item_user_data("webcam_texture")
        image = (recovered_texture_data * 255.0).astype(np.uint8)
        image = image.reshape((240, 320, 3))
        frame_rgb = image

        #process with mediapip
        results = self.objectron.process(frame_rgb)
        #print(results)

        if (results.detected_objects):
            #print(results.detected_objects)
            for detected_object in results.detected_objects:
                self.mp_drawing.draw_landmarks(frame_rgb, detected_object.landmarks_2d, self.mp_objectron.BOX_CONNECTIONS)

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


def create_node(node_class, parent, node_dictionary, nodes_ids):
    tag = str(node_class.__name__)
    if (tag in node_dictionary):
        print("already exists")
        return
    node_new_id = len(node_dictionary.items())
    while(node_new_id in nodes_ids):
        node_new_id = len(node_dictionary.items()) + (random.random() % 100)

    new_node = node_class(parent=parent, tag=tag, unique_id=node_new_id)
    node_dictionary[new_node.tag] = new_node
    node_dictionary[new_node.tag].node_unique_id = node_new_id
