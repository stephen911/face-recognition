from tkinter import messagebox
import dlib
import numpy as np
import cv2
import os
import shutil
import time
import logging
import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk
import features_extraction_to_csv
# import attendance_taker
# import app
import webbrowser
import subprocess

# Use frontal face detector of Dlib
detector = dlib.get_frontal_face_detector()


class Face_Register:
    def __init__(self):

        self.current_frame_faces_cnt = 0  # cnt for counting faces in the current frame
        self.existing_faces_cnt = 0  # cnt for counting saved faces
        self.ss_cnt = 0  # cnt for screenshots

        # Tkinter GUI
        self.win = tk.Tk()
        self.win.title("Face Register")

        # Please modify the window size here if needed
        self.win.geometry("1000x500")

        # GUI left part
        self.frame_left_camera = tk.Frame(self.win)
        self.label = tk.Label(self.win)
        self.label.pack(side=tk.LEFT)
        self.frame_left_camera.pack()

        # GUI right part
        self.frame_right_info = tk.Frame(self.win)
        self.label_cnt_face_in_database = tk.Label(self.frame_right_info, text=str(self.existing_faces_cnt))
        self.label_fps_info = tk.Label(self.frame_right_info, text="")
        self.input_name = tk.Entry(self.frame_right_info)
        self.input_id = tk.Entry(self.frame_right_info)  # Add input field for ID number
        self.input_name_char = ""
        self.label_warning = tk.Label(self.frame_right_info)
        self.label_face_cnt = tk.Label(self.frame_right_info, text="Faces in the current frame: ")
        self.log_all = tk.Label(self.frame_right_info)

        self.font_title = tkFont.Font(family='Helvetica', size=20, weight='bold')
        self.font_step_title = tkFont.Font(family='Helvetica', size=15, weight='bold')
        self.font_warning = tkFont.Font(family='Helvetica', size=15, weight='bold')

        self.path_photos_from_camera = "data/data_faces_from_camera/"
        self.current_face_dir = ""
        self.font = cv2.FONT_ITALIC

        # Current frame and face ROI position
        self.current_frame = np.ndarray
        self.face_ROI_image = np.ndarray
        self.face_ROI_width_start = 0
        self.face_ROI_height_start = 0
        self.face_ROI_width = 0
        self.face_ROI_height = 0
        self.ww = 0
        self.hh = 0

        self.out_of_range_flag = False
        self.face_folder_created_flag = False

        # FPS
        self.frame_time = 0
        self.frame_start_time = 0
        self.fps = 0
        self.fps_show = 0
        self.start_time = time.time()

        self.cap = cv2.VideoCapture(0)  # Get video stream from the camera

        # self.cap = cv2.VideoCapture("test.mp4")   # Input local video

    # Delete old face folders
    def GUI_clear_data(self):
        # "/data_faces_from_camera/person_x/"...
        folders_rd = os.listdir(self.path_photos_from_camera)
        for i in range(len(folders_rd)):
            shutil.rmtree(self.path_photos_from_camera + folders_rd[i])
        if os.path.isfile("data/features_all.csv"):
            os.remove("data/features_all.csv")
        self.label_cnt_face_in_database['text'] = "0"
        self.existing_faces_cnt = 0
        self.log_all["text"] = "Face images and `features_all.csv` removed!"
        
    def show(self):
        subprocess.Popen(["python", "app.py"]) 
        url = "http://127.0.0.1:5000/"
        webbrowser.open(url, new=0, autoraise=True)

    def GUI_get_input_name(self):
        name = self.input_name.get().strip()  # Get the name input and remove leading/trailing spaces
        id_number = self.input_id.get().strip()  # Get the ID input and remove leading/trailing spaces

        if not name or not id_number:
            # Display an error message if one or both fields are empty
            self.log_all["text"] = "Both Name and ID fields are required"
            return

        self.input_name_char = f"{name}_{id_number}"  # Concatenate name and ID number
        self.create_face_folder()
        self.label_cnt_face_in_database['text'] = str(self.existing_faces_cnt)
        
    # def start_flask_server(self):
    #     # Run the Flask server as a subprocess
    #     subprocess.Popen(["python", "app.py"]) 
    #     messagebox.showinfo("showinfo", "Server started. click on show attendance to continue")  
        
        
    def take_attendance(self):
        # Run the Flask server as a subprocess
        subprocess.Popen(["python", "attendance_taker.py"]) 


    def GUI_info(self):
        tk.Label(self.frame_right_info,
                 text="Face register",
                 font=self.font_title).grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=2, pady=20)

        tk.Label(self.frame_right_info, text="FPS: ").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.label_fps_info.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(self.frame_right_info, text="Faces in database: ").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.label_cnt_face_in_database.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(self.frame_right_info,
                 text="Faces in the current frame: ").grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        self.label_face_cnt.grid(row=3, column=2, columnspan=3, sticky=tk.W, padx=5, pady=2)

        self.label_warning.grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)
        # tk.Button(self.frame_right_info,
        #           text='Start Server',
        #           command=self.start_flask_server,
        #   bg='#90EE90').grid(row=4, column=1, columnspan=3, sticky=tk.W, padx=5, pady=2)

        # # Step 1: Clear old data
        # tk.Label(self.frame_right_info,
        #          font=self.font_step_title,
        #          text="Step 1: Clear face photos").grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=20)
        # tk.Button(self.frame_right_info,
        #           text='Clear',
        #           command=self.GUI_clear_data).grid(row=6, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)

        
                # Step 1: Clear old data
        tk.Label(self.frame_right_info,
                 font=self.font_step_title,
                 text="Step 1: Take Asttendance").grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=20)
        
        self.reg = tk.Button(self.frame_right_info,
                  text='Register Students',
                  command=self.process)
        
        self.reg.grid(row=6, column=2, columnspan=3, sticky=tk.W, padx=5, pady=2)
        tk.Button(self.frame_right_info,
                  text='Take Attendance',
                  command=self.take_attendance).grid(row=6, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)
        
        
        # tk.Label(self.frame_right_info,
        #          font=self.font_step_title,
        #          text="Step 1: Show Attendance").grid(row=5, column=2, columnspan=2, sticky=tk.W, padx=5, pady=20)
        
        tk.Button(self.frame_right_info,
                  text='Show Attendance',
                  command=self.show).grid(row=6, column=1, columnspan=3, sticky=tk.W, padx=5, pady=2)
        # Step 2: Input name and create folders for face
        tk.Label(self.frame_right_info,
                 font=self.font_step_title,
                 text="Step 2: Input name and ID").grid(row=7, column=0, columnspan=2, sticky=tk.W, padx=5, pady=20)

        tk.Label(self.frame_right_info, text="Name: ").grid(row=8, column=0, sticky=tk.W, padx=5, pady=0)
        self.input_name.grid(row=8, column=1, sticky=tk.W, padx=0, pady=2)

        tk.Label(self.frame_right_info, text="ID: ").grid(row=9, column=0, sticky=tk.W, padx=5, pady=0)
        self.input_id.grid(row=9, column=1, sticky=tk.W, padx=0, pady=2)

        tk.Button(self.frame_right_info,
                  text='Input',
                  command=self.GUI_get_input_name).grid(row=9, column=2, padx=5)

        # Step 3: Save the current face in the frame
        tk.Label(self.frame_right_info,
                 font=self.font_step_title,
                 text="Step 3: Save face image").grid(row=10, column=0, columnspan=2, sticky=tk.W, padx=5, pady=20)

        tk.Button(self.frame_right_info,
                  text='Save current face',
                  command=self.save_current_face).grid(row=11, column=0, columnspan=3, sticky=tk.W)
        
        tk.Button(self.frame_right_info,
              text='Train Model',
              command=features_extraction_to_csv.main).grid(row=11, column=2, columnspan=3, sticky=tk.W)

        # Show log in GUI
        self.log_all.grid(row=13, column=0, columnspan=20, sticky=tk.W, padx=5, pady=20)

        self.frame_right_info.pack()

    # Mkdir for saving photos and CSV
    def pre_work_mkdir(self):
        # Create folders to save face images and CSV
        if os.path.isdir(self.path_photos_from_camera):
            pass
        else:
            os.mkdir(self.path_photos_from_camera)

    # Start from person_x+1
    def check_existing_faces_cnt(self):
        if os.listdir("data/data_faces_from_camera/"):
            # Get the order of the latest person
            person_list = os.listdir("data/data_faces_from_camera/")
            person_num_list = []
            for person in person_list:
                person_order = person.split('_')[1].split('_')[0]
                person_num_list.append(int(person_order))
            self.existing_faces_cnt = max(person_num_list)

        # Start from person_1
        else:
            self.existing_faces_cnt = 0

    # Update FPS of the video stream
    def update_fps(self):
        now = time.time()
        # Refresh FPS per second
        if str(self.start_time).split(".")[0] != str(now).split(".")[0]:
            self.fps_show = self.fps
        self.start_time = now
        self.frame_time = now - self.frame_start_time
        self.fps = 1.0 / self.frame_time
        self.frame_start_time = now

        self.label_fps_info["text"] = str(self.fps.__round__(2))

    def create_face_folder(self):
        # Create the folders for saving faces
        self.existing_faces_cnt += 1
        if self.input_name_char:
            self.current_face_dir = self.path_photos_from_camera + \
                                    "person_" + str(self.existing_faces_cnt) + "_" + \
                                    self.input_name_char
        else:
            self.current_face_dir = self.path_photos_from_camera + \
                                    "person_" + str(self.existing_faces_cnt)
        os.makedirs(self.current_face_dir)
        self.log_all["text"] = "\"" + self.current_face_dir + "/\" created!"
        logging.info("\n%-40s %s", "Create folders:", self.current_face_dir)

        self.ss_cnt = 0  # Clear the cnt of screenshots
        self.face_folder_created_flag = True  # Face folder already created

    def save_current_face(self):
        if self.face_folder_created_flag:
            if self.current_frame_faces_cnt == 1:
                if not self.out_of_range_flag:
                    for i in range(1, 11):  # Adjusted loop range to capture 10 images
                        self.ss_cnt += 1
                        # Create a blank image according to the size of the face detected
                        self.face_ROI_image = np.zeros((int(self.face_ROI_height * 2), self.face_ROI_width * 2, 3),
                                                        np.uint8)
                        for ii in range(self.face_ROI_height * 2):
                            for jj in range(self.face_ROI_width * 2):
                                self.face_ROI_image[ii][jj] = self.current_frame[self.face_ROI_height_start - self.hh + ii][
                                    self.face_ROI_width_start - self.ww + jj]
                        self.log_all["text"] = "\"" + self.current_face_dir + "/img_face_" + str(
                            self.ss_cnt) + ".jpg\"" + " saved!"
                        self.face_ROI_image = cv2.cvtColor(self.face_ROI_image, cv2.COLOR_BGR2RGB)


                        # cv2.putText(self.face_ROI_image, f'Images Captured: {i}/10', (60, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                        cv2.imwrite(self.current_face_dir + "/img_face_" + str(self.ss_cnt) + ".jpg",
                                    self.face_ROI_image)
                        self.label_warning["text"] = f'Images Captured: {i}/10'
                        self.label_warning['fg'] = 'red'
                        self.out_of_range_flag = True
                        # color_rectangle = (255, 0, 0)
                        logging.info("%-40s %s/img_face_%s.jpg", "Save into：",
                                    str(self.current_face_dir), str(self.ss_cnt) + ".jpg")
                    self.log_all["text"] = "10 images saved!"
                    messagebox.showinfo("showinfo", "10 images saved!") 
                else:
                    self.log_all["text"] = "Please do not go out of range!"
            else:
                self.log_all["text"] = "No face in the current frame!"
        else:
            self.log_all["text"] = "Please run step 2!"



    def get_frame(self):
        try:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                frame = cv2.resize(frame, (640, 480))
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except:
            print("Error: No video input!!!")

    # Main process of face detection and saving
    def process(self):
        ret, self.current_frame = self.get_frame()
        faces = detector(self.current_frame, 0)
        
        # Get frame
        if ret:
            self.update_fps()
            self.label_face_cnt["text"] = str(len(faces))
            
            # Face detected
            if len(faces) != 0:
                # Show the ROI of faces
                for k, d in enumerate(faces):
                    self.face_ROI_width_start = d.left()
                    self.face_ROI_height_start = d.top()
                    
                    # Compute the size of the rectangle box
                    self.face_ROI_height = (d.bottom() - d.top())
                    self.face_ROI_width = (d.right() - d.left())
                    self.hh = int(self.face_ROI_height / 2)
                    self.ww = int(self.face_ROI_width / 2)

                    # If the size of ROI > 480x640
                    if (d.right() + self.ww) > 640 or (d.bottom() + self.hh > 480) or (d.left() - self.ww < 0) or (
                            d.top() - self.hh < 0):
                        self.label_warning["text"] = "OUT OF RANGE"
                        self.label_warning['fg'] = 'red'
                        self.out_of_range_flag = True
                        color_rectangle = (255, 0, 0)
                    else:
                        self.out_of_range_flag = False
                        self.label_warning["text"] = ""
                        color_rectangle = (255, 255, 255)
                    
                    # Draw rectangle on the current frame
                    cv2.rectangle(self.current_frame,
                                tuple([d.left() - self.ww, d.top() - self.hh]),
                                tuple([d.right() + self.ww, d.bottom() + self.hh]),
                                color_rectangle, 2)
                    
                # Add alert message to the current frame
                cv2.putText(self.current_frame, self.label_warning["text"], (30, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                
            # Display the number of images taken and the total number of images to be taken
            # cv2.putText(self.current_frame, f'Images Captured: {self.ss_cnt}/10', (30, 60),
            #             cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 20), 2)
            
            self.current_frame_faces_cnt = len(faces)

            # Convert PIL.Image.Image to PIL.Image.PhotoImage
            img_Image = Image.fromarray(self.current_frame)
            img_PhotoImage = ImageTk.PhotoImage(image=img_Image)
            self.label.img_tk = img_PhotoImage
            self.label.configure(image=img_PhotoImage)
            
            self.reg.config(state="disabled")
            

        # Refresh frame
        self.win.after(20, self.process)



    def run(self):
        self.pre_work_mkdir()
        self.check_existing_faces_cnt()
        self.GUI_info()
        # self.process()
        self.win.mainloop()


def main():
    logging.basicConfig(level=logging.INFO)
    Face_Register_con = Face_Register()
    Face_Register_con.run()


if __name__ == '__main__':
    main()
