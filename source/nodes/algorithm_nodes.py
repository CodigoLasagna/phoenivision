import dearpygui.dearpygui as dpg
#import numpy as np
from . import base_node as BN
from ..theming.base_theme_confs import Themer
#import cv2 as cv
import numpy as np
import pandas as pd

from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
#from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
#from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
#from sklearn.linear_model import Perceptron
#from sklearn.linear_model import RidgeClassifier
#from sklearn.linear_model import PassiveAggressiveClassifier
#from sklearn.linear_model import LogisticRegression

#from sklearn.metrics import accuracy_score
#from sklearn.metrics import confusion_matrix
#from sklearn.metrics import classification_report
#from sklearn.metrics import roc_curve, auc
#from sklearn.preprocessing import StandardScaler
#from sklearn.model_selection import cross_val_score

import joblib
from ast import literal_eval

import time
import csv
from pathlib import Path

class StaticModelMaker(BN.BaseNode):
    def __init__(self, parent, tag, unique_id):
        super().__init__(parent, tag, unique_id)
        self.node_type = BN.NodeType.MODEL_LAYER_NODE
        self.tag = self.tag + "_" + str(self.node_unique_id)
        self.create_node()
        mouse_pos = dpg.get_mouse_pos(local=False)
        mouse_pos[0] = mouse_pos[0] - 180
        mouse_pos[1] = mouse_pos[1] - 120
        dpg.set_item_pos(self.tag, mouse_pos)
        self.children_tags.append(self.tag+"_in_tag_db")
        self.children_tags.append(self.tag+"_in_tag_img")
        self.children_tags.append(self.tag+"_out_tag")
        self.models_dir = "./app_data/models/"
        self.database_dir = "./app_data/databases/"

        self.formed_path = self.models_dir+"KNeighbors/"
        self.path_to_pass = ""
        self.models_open_path = Path(self.models_dir)
        self.dbs_open_path = Path(self.database_dir)
        self.formed_path_open = Path(self.formed_path)
        self.current_data_type = 0
        self.received_tracked_data = []
        self.received_db_info_data = []
        self.capturing = False
        self.loaded_model = None
        self.current_features_labels = []
        self.x_train = None
        self.x_test = None
        self.y_train = None
        self.y_test = None
        self.model_to_train = 0


    def create_node(self):
        if (dpg.does_item_exist(self.tag)):
            return
        with dpg.node(label="StaticModelMaker", tag=self.tag, parent=self.parent):
            with dpg.node_attribute(label="input_db", attribute_type=dpg.mvNode_Attr_Input, tag=self.tag+"_in_tag_db"):
                dpg.add_text("Input DB")
            with dpg.node_attribute(label="input_img", attribute_type=dpg.mvNode_Attr_Input, tag=self.tag+"_in_tag_img"):
                dpg.add_text("Input BGR Image")
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.group(tag=self.tag+"extra_panel", width=530, height=32):
                    pass
                dpg.bind_item_theme(self.tag+"extra_panel", Themer.create_color_window_theme())


            with dpg.node_attribute(label="output_att", attribute_type=dpg.mvNode_Attr_Output, tag=self.tag+"_out_tag"):
                dpg.add_text("Data output")
        self.gen_extra_items()

    def gen_extra_items(self):
        dpg.add_radio_button(
            parent=self.tag + "extra_panel",
            items=["Nuevo Modelo", "Cargar Modelo"],
            horizontal=True,
            callback=self.toggle_sections,
            tag=self.tag + "data_col_radio"
        )
        dpg.add_combo(
            parent=self.tag + "extra_panel",
            default_value="Model type",
            #items=["KNeighbors", "SVC", "Kmeans"],
            items=[
                "KNeighbors",
                "SVC",
                "DecisionTree",
                "RandomForest",
                "MLPClassifier",
                "GradientBoosting",
                "AdaBoost",
                "GNB", # Gaussian Naive Bayes
            ],
            #horizontal=True,
            callback=lambda sender: self.load_specific_model_list(dpg.get_value(sender)),
            tag=self.tag + "model_list_radio_selector"
        )

        
        # Grupo para "Nuevo modelo"
        with dpg.group(parent=self.tag + "extra_panel", tag=self.tag + "extra_panel_radio_new_model", show=True, height=35):
            with dpg.table(header_row=False):
                dpg.add_table_column(width_fixed=True)
                dpg.add_table_column(width_fixed=True)

                with dpg.table_row():
                    dpg.add_text("Nombre del Modelo: ")
                    dpg.add_input_text(width=360, tag=self.tag+"model_name_file")



            #temp_item = dpg.add_button(label="Capturar datos", callback=self.save_timed_snapshots)
            #dpg.bind_item_theme(temp_item, Themer.create_yellow_btn_theme())

            #temp_item = dpg.add_button(label="Cargar Datos", tag=self.tag+"load_data", callback=lambda: self.load_data_from_db(loader_part=0))
            #dpg.bind_item_theme(self.tag+"load_data", Themer.create_blue_btn_theme())
        
        # Grupo para "Cargar modelo"
        with dpg.group(parent=self.tag + "extra_panel", tag=self.tag + "extra_panel_radio_load_model", show=False):
            dpg.add_combo(
                default_value="Cargar Modelo",
                #items=["Eliminar"],
                callback=lambda sender: self.load_model_list(dpg.get_value(sender)),
                tag=self.tag+"models_list_item"
            ),

            dpg.add_combo(
                default_value="Cargar DB",
                callback=lambda sender: self.load_db_list(dpg.get_value(sender)),
                tag=self.tag+"dbs_list_item"
            ),
            #with dpg.menu(label="Pattern recognition"):
            #    dpg.add_menu_item(label="Webcam hands i/o node")
            #    with dpg.menu(label="face recognition"):
            #        pass

            dpg.add_button(parent=self.tag + "extra_panel", label="status", tag=self.tag+"status_node_tag")
            dpg.bind_item_theme(self.tag+"status_node_tag", Themer.create_contour_color_text())

            dpg.add_button(parent=self.tag + "extra_panel", label="prediction", tag=self.tag+"pred_tag")
            dpg.bind_item_theme(self.tag+"pred_tag", Themer.create_contour_color_text([155, 171, 178]))

            dpg.add_button(parent=self.tag + "extra_panel", label="Entrenar Modelo", tag=self.tag+"save_db_btn", callback=self.train_model)
            dpg.bind_item_theme(self.tag+"save_db_btn", Themer.create_green_btn_theme())

    def load_specific_model_list(self, sender):
        self.formed_path = self.models_dir+sender+"/"
        self.formed_path_open = Path(self.formed_path)
        csv_dbs = [file.name for file in self.formed_path_open.iterdir() if file.suffix == '.pkl']
        dpg.configure_item(self.tag+"models_list_item", items=csv_dbs)
        if (sender == "KNeighbors"):
            self.model_to_train = 0
        if (sender == "SVC"):
            self.model_to_train = 1
        if (sender == "DecisionTree"):
            self.model_to_train = 2
        if (sender == "RandomForest"):
            self.model_to_train = 3
        if (sender == "MLPClassifier"):
            self.model_to_train = 4
        if (sender == "GradientBoosting"):
            self.model_to_train = 5
        if (sender == "AdaBoost"):
            self.model_to_train = 6
        if (sender == "GNB"):
            self.model_to_train = 7

    def train_model(self):
        model_name_file = dpg.get_value(self.tag + "model_name_file")
        if len(model_name_file) <= 0:
            dpg.configure_item(self.tag + "status_node_tag", label="Nombre no válido")
            dpg.bind_item_theme(self.tag + "status_node_tag", Themer.create_contour_color_text([240, 79, 120]))
            return
        else:
            model_name_file = model_name_file.replace(' ', '_')
    
        if len(self.received_db_info_data) <= 0:
            dpg.configure_item(self.tag + "status_node_tag", label="Base de datos no cargada")
            dpg.bind_item_theme(self.tag + "status_node_tag", Themer.create_contour_color_text([240, 79, 120]))
            return
    
        self.x_train, self.x_test, self.y_train, self.y_test = self.obtain_test_variables_from_db(self.received_db_info_data)
    
        training_model = None
        if (self.model_to_train == 0):
            training_model = KNeighborsClassifier(n_neighbors=13, weights='distance')

        if (self.model_to_train == 1):
            training_model = SVC(C=1, kernel='rbf', gamma='scale', probability=True)

        if (self.model_to_train == 2):
            training_model = DecisionTreeClassifier(random_state=42)

        if (self.model_to_train == 3):
            training_model = RandomForestClassifier(n_estimators=100, random_state=42)

        if (self.model_to_train == 4):
            training_model = MLPClassifier(
                hidden_layer_sizes=(100, ),
                activation='relu',
                solver='adam',
                learning_rate='constant',
                max_iter=200,
                random_state=42
            )
        if (self.model_to_train == 5):
            training_model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=3,
                random_state=42
            )
        if (self.model_to_train == 6):
            training_model = AdaBoostClassifier(
                n_estimators=50,
                learning_rate=1.0,
                random_state=42
            )
        if (self.model_to_train == 7):
            training_model = GaussianNB()

        training_model.fit(self.x_train, self.y_train)
    
        joblib.dump(training_model, self.formed_path+model_name_file+".pkl")
        self.load_model()

        dpg.configure_item(self.tag+"status_node_tag", label="Modelo: ["+model_name_file+".pkl] guardado con exito.")
        dpg.bind_item_theme(self.tag+"status_node_tag", Themer.create_contour_color_text([127, 218, 37]))

    def obtain_test_variables_from_db(self, db_dir):
        db_csv = pd.read_csv(db_dir, skiprows=1)
        target_column = "tag"
        feature_labels = [col for col in db_csv.columns if col != target_column]
        self.current_features_labels = feature_labels
    
        for f_label in feature_labels:
            db_csv[f_label] = db_csv[f_label].apply(literal_eval)
    
        db_csv['features'] = db_csv.apply(
            lambda row: {key.upper(): row[key] for key in feature_labels}, axis=1
        )
        db_csv['features'] = db_csv['features'].apply(self.flatten_features)
    
        # Asegurar que todas las características tengan la misma longitud
        max_length = max(len(features) for features in db_csv['features'])
        db_csv['features'] = db_csv['features'].apply(
            lambda features: features + [0] * (max_length - len(features))
        )
    
        x_val = np.array(db_csv['features'].to_list())
        y_val = db_csv['tag'].to_list()
    
        return train_test_split(x_val, y_val, test_size=0.3, random_state=42)

    def load_model_list(self, sender):
        dpg.set_value(self.tag + "model_name_file", sender.replace('.pkl', ''))
        self.load_model()

    def load_db_list(self, sender):
        db_file_dir = self.database_dir + "/" + sender
        db_csv = pd.read_csv(db_file_dir, skiprows=1)
        target_column = "tag"
        feature_labels = [col for col in db_csv.columns if col != target_column]
        self.current_features_labels = feature_labels

        self.x_train, self.x_test, self.y_train, self.y_test = self.obtain_test_variables_from_db(db_file_dir)


    def load_model(self):
        model_name_file = dpg.get_value(self.tag + "model_name_file")
        model_name_file = model_name_file.replace(' ', '_')
        self.loaded_model = joblib.load(self.formed_path+model_name_file+".pkl")
        if hasattr(self.loaded_model, 'probability') and not self.loaded_model.probability:
            self.loaded_model.probability = True

    def predict_data(self):
        if (self.loaded_model == None):
            time.sleep(0.01)
            return
        #print("test")
        #print(len(self.received_tracked_data))
        #print(self.current_features_labels)
        #print(len(self.current_features_labels))
        #print(self.current_features_labels)
        if (len(self.received_tracked_data) <= 0):
            time.sleep(0.01)
            return
        #print("test2")
        prepared_data = {}
        count_i = 0
        for f_label in self.current_features_labels:
            prepared_data[f_label.upper()] = self.received_tracked_data[count_i]
            count_i+= 1
        #print(prepared_data)
        x_data = self.flatten_features(prepared_data) #adjusted data
        #print(x_data)
        is_none = False
        sum = 0
        for x_val in x_data:
            sum += x_val
        if (sum == 0):
            is_none = True
            #is_none = False
            

        #print(x_data)
        if (len(x_data) > 0 and not is_none):
            x_data = np.array(x_data)
            x_data = x_data.reshape(1, -1)

            y_pred = self.loaded_model.predict(x_data)
            probabilities = self.loaded_model.predict_proba(x_data)
            max_prob = max(probabilities[0])
            dpg.configure_item(self.tag + "pred_tag", label=y_pred[0]+f"({max_prob * 100:.2f}%)")
            #max(probabilities[0])
            #accuracy = 1 if (y_pred[0])
            #accuracy = accuracy_score(self.y_test, y_pred)
            #print()
            time.sleep(0.005)
        else:
            dpg.configure_item(self.tag + "pred_tag", label='None')
            time.sleep(0.01)


            #print(f"Predicted: {y_pred}")
    
    def flatten_features(self, features):
        flat = []
        for key, value in features.items():
            if isinstance(value, list):  # Procesar solo si es una lista
                if value:  # Comprobar que no esté vacía
                    x_coords = [point[0] for point in value if isinstance(point, tuple) and len(point) == 3]
                    y_coords = [point[1] for point in value if isinstance(point, tuple) and len(point) == 3]
                    z_coords = [point[2] for point in value if isinstance(point, tuple) and len(point) == 3]
    
                    # Calcular las medias para X, Y, Z
                    mean_x = np.mean(x_coords) if x_coords else 0
                    mean_y = np.mean(y_coords) if y_coords else 0
                    mean_z = np.mean(z_coords) if z_coords else 0
    
                    # Agregar las medias al vector de características
                    flat.extend([mean_x, mean_y, mean_z])
                else:
                    # Si la lista está vacía, agregar valores predeterminados (0, 0, 0)
                    flat.extend([0, 0, 0])
            else:
                print(f"Advertencia: La clave '{key}' no tiene una lista como valor.")
        return flat

    def preprocess_real_time_data(self, real_time_data):
        # Suponiendo que `real_time_data` es un diccionario con las mismas claves que el conjunto de entrenamiento
        self.current_features_labels = ['keypoints_left', 'keypoints_right']
        # Estructura los datos como un diccionario con las características
        processed_data = []
        
        for data_set in real_time_data:
            # Para cada conjunto de datos (tuplas)
            data_dict = {}
            for i, feature in enumerate(data_set):
                for j, value in enumerate(feature):
                    data_dict[self.current_features_labels[j]] = value
            processed_data.append(data_dict)
        
        return processed_data  # El modelo espera una entrada 2D


    #def initialize_csv(self):
    #    fixed_file_name = dpg.get_value(self.tag+"db_name_file")
    #    fixed_file_name = fixed_file_name.replace(" ", "_")
    #    file_to_open = Path(self.models_dir+"/"+fixed_file_name+".csv")
    #    if (len(fixed_file_name) < 1):
    #        dpg.configure_item(self.tag+"status_node_tag", label="Nombre no valido")
    #        dpg.bind_item_theme(self.tag+"status_node_tag", Themer.create_contour_color_text([240, 79, 120]))
    #        return
    #    if not (file_to_open.exists()):
    #        csvfile = (open(file_to_open, 'w', newline=''))
    #        dpg.configure_item(self.tag+"status_node_tag", label="Base de datos registrada")
    #        dpg.bind_item_theme(self.tag+"status_node_tag", Themer.create_contour_color_text([127, 218, 37]))
    #    else:
    #        return
    #    if (self.current_data_type == 0):
    #        writer = csv.writer(csvfile)
    #        writer.writerow([self.current_data_type])
    #        writer.writerow(['tag', 'keypoints_left_hand', 'keypoints_right_hand'])

    def load_existing_models(self):
        pkl_models = [file.name for file in self.formed_path_open.iterdir() if file.suffix == '.pkl']
        dpg.configure_item(self.tag+"models_list_item", items=pkl_models)

    def load_existing_dbs(self):
        csv_dbs = [file.name for file in self.dbs_open_path.iterdir() if file.suffix == '.csv']
        dpg.configure_item(self.tag+"dbs_list_item", items=csv_dbs)


    def toggle_sections(self, sender, app_data):
        if app_data == "Nuevo Modelo":
            dpg.configure_item(self.tag + "extra_panel_radio_new_model", show=True)
            dpg.configure_item(self.tag + "extra_panel_radio_load_model", show=False)
        else:
            dpg.configure_item(self.tag + "extra_panel_radio_new_model", show=False)
            dpg.configure_item(self.tag + "extra_panel_radio_load_model", show=True)
            self.load_existing_models()
            self.load_existing_dbs()


    def update_input_atts(self):
        track_recovered_data = []
        db_info_recovered_data = ""
        #all_inputs = False
        if (len(self.connected_input_nodes.values()) > 0):
            check_node = list(self.connected_input_nodes.values())[0]
            if (check_node.node_type == BN.NodeType.DATA_PROC_NODE):
                db_info_recovered_data = check_node.node_output_data
            if (check_node.node_type == BN.NodeType.PATTER_REC_NODE):
                track_recovered_data = check_node.node_output_data
        if (len(self.connected_input_nodes.values()) > 1):
            check_node = list(self.connected_input_nodes.values())[1]
            if (check_node.node_type == BN.NodeType.DATA_PROC_NODE):
                db_info_recovered_data = check_node.node_output_data
            if (check_node.node_type == BN.NodeType.PATTER_REC_NODE):
                track_recovered_data = check_node.node_output_data
            #all_inputs = True

        if (track_recovered_data != None):
            if (len(track_recovered_data) > 0): #check for type of data
                if (self.current_data_type != track_recovered_data[0]):
                    self.current_data_type = track_recovered_data[0]
                if (len(track_recovered_data[1]) > 0):
                    self.received_tracked_data = track_recovered_data[1] # realtime data from recon node
                    #print(self.received_tracked_data)

        if (db_info_recovered_data != None and len(db_info_recovered_data) > 1):
            if (self.received_db_info_data != db_info_recovered_data): # update on chage from db
                self.received_db_info_data = db_info_recovered_data
            #print(self.received_db_info_data)
        #print(self.received_db_info_data)
        self.predict_data()


    def update_output_atts(self, stop_thread):
        if (self.update_loop == True):
            return
        self.update_loop = True
        while not(stop_thread.is_set()):
            if not(self.lock):
                break
        self.update_loop = False
