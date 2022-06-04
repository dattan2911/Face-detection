# File used for display UI recogzation
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel, Label, Button

from importlib_metadata import entry_points
from PIL import Image, ImageTk
import cv2
import gc
import time
import faces_recognizer  #file contain all method for face recognizer
import file_handlers #file use to read/write pkl file
import os
import numpy as np
cap = cv2.VideoCapture(0)


APP_WIDTH = 920 #minimal width of the GUI
APP_HEIGHT = 534 #minimal height of the gui
WIDTH  = int(cap.get(3)) #webcam's picture width
HEIGHT = int(cap.get(4)) #webcam's picture height

#how many face-encodings to be created of each new face 
NUMBER_OF_FACES_ENCODINGS = 1
NAME_ADDED = False

RECOGNIZE = False

# use to create and add file pkl into KNOWN_FACES_DIRECTORY
def add_to_database(KNOWN_FACES, name):
	KNOWN_FACES[name] = faces_recognizer.KNOWN_FACES_ENCODINGS
	file_handlers.create_file(name)
	file_handlers.save_encodings(name)
	#update the current known faces dict with the freshly 
	#added faces' encodings
	KNOWN_FACES = file_handlers.load_known_faces() 
	return KNOWN_FACES

def refresh_database(name):
	KNOWN_FACES = {}
	for _ in range(NUMBER_OF_FACES_ENCODINGS):
		_, frame = cap.read()
		if frame is not None:
			faces_recognizer.KNOWN_FACES_ENCODINGS, NUMBER_OF_FACES_IN_FRAME = faces_recognizer.create_face_encodings(frame)

			if len(faces_recognizer.KNOWN_FACES_ENCODINGS) and NUMBER_OF_FACES_IN_FRAME==1:
				KNOWN_FACES = add_to_database(KNOWN_FACES, name)
				name_entry.delete(0, 'end')
				
			else:
				
				messagebox.showinfo(message='Either no face, or multiple faces has been detected!\nPlease try again when problem resolved.',
									title = "Invalid name")
				name_entry.delete(0, 'end')
				name_entry.focus()
	return KNOWN_FACES

def add_new_known_face():
	faces_recognizer.KNOWN_FACES = refresh_database(name = NEW_NAME.get().lower())
	faces_recognizer.KNOWN_FACES = file_handlers.load_known_faces()

def display_frames_per_second(frame, start_time):
	END_TIME = abs(start_time-time.time())
	TOP_LEFT = (0,0)
	BOTTOM_RIGHT = (116,26)
	TEXT_POSITION = (8,20)
	TEXT_SIZE = 0.6
	FONT = cv2.FONT_HERSHEY_SIMPLEX
	COLOR = (255,255,0) #BGR
	cv2.rectangle(frame, TOP_LEFT, BOTTOM_RIGHT, (0,0,0), cv2.FILLED)
	cv2.putText(frame, "FPS: {}".format(round(1/max(0.0333,END_TIME),1)), TEXT_POSITION, FONT, TEXT_SIZE,COLOR)
	return frame

#convert a fame object to an image object
def convert_to_image(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    contrast = 1.25
    brightness = 60
    frame[:,:,2] = np.clip(contrast * frame[:,:,2] + brightness, 0, 255)
    frame = cv2.cvtColor(frame, cv2.COLOR_HSV2RGB)
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(frame)
    # image = cv2.normalize(frame, frame, 0, 255, cv2.NORM_MINMAX)
    return image

def recognize_faces (frame):
	frame = faces_recognizer.identify_faces(frame)
	return frame
#the main function

def update_frame():
	START_TIME = time.time()
	global image
	_, frame = cap.read()
	if frame is not None:
		frame = cv2.flip(frame, 1)
		if RECOGNIZE:
			frame = recognize_faces(frame)
		frame = display_frames_per_second(frame, START_TIME)
		image = convert_to_image(frame)
	photo.paste(image)
	root.after(round(10), update_frame) 


#check that name is exit
def name_authentification():
	global NAME_ADDED
	if NEW_NAME.get().lower() in faces_recognizer.KNOWN_FACES.keys() or not len(NEW_NAME.get()):
		messagebox.showinfo(message='Name is exist!\t\nPlease try again.', title = "Invalid name")
		name_entry.delete(0, 'end')
		name_entry.focus()
		NAME_ADDED = False
	if NAME_ADDED:
		return True



def enter_name(*args):
	global NAME_ADDED
	NEW_NAME.get()
	NAME_ADDED = True
	if name_authentification(): 
		add_new_known_face()



def enable_recognition():
	global RECOGNIZE
	if RECOGNIZE:
		RECOGNIZE = False
		recognition_button["bg"] = "black"
		name_button["state"]="disable"
		name_entry["state"]="disable"
	else:
		RECOGNIZE = True
		recognition_button["bg"] = "red"
		name_button["state"]="enable"
		name_entry["state"]="enable"
        
def credit():
    top = Toplevel( )
    top.title('Credit')
    lbl=Label(top, text="Group 2 member:").pack()
    name1=Label(top, text="Lê Quang Duy - 19110072").pack()
    name2=Label(top, text="Huỳnh Nguyên Khang - 19110144").pack()
    name3=Label(top, text="Tân Tiến Đạt - 19110117").pack()
    closeBtn=Button(top, text="Close", command = top.destroy).pack()
    
# load all the known faces in the database to the KNOWN_FACES dict
faces_recognizer.KNOWN_FACES = file_handlers.load_known_faces()

# start of GUI
root = tk.Tk()



root.title("Recognition Cam")
root.minsize(APP_WIDTH,APP_HEIGHT)
root["bg"]="#A068F8"


# GUI elements 


canvas = tk.Canvas(root, width=WIDTH-5, height=HEIGHT-5,bg="black")
canvas.place(relx=0.03,rely=0.1)

# Label
label= tk.Label(root, text="Face Recognition by Group 2", font= ("FONT_HERSHEY_SIMPLEX",20),bg="#A068F8")
label.place(relx=0.3,rely=0.012)
# Recognize button
recognition_button = tk.Button(canvas, text = "Recognize", command = enable_recognition,bg = "black", fg = "white", activebackground = 'white')
recognition_button.place(relx=0.87,rely=0.93, relwidth=0.12,relheight=0.06)
recognition_button.bind(enable_recognition)
recognition_button.focus()

#  Name input field and button
NEW_NAME = tk.StringVar()
name_entry = ttk.Entry(root, textvariable=NEW_NAME, state="disable")
name_entry.place(relx=0.97, rely=0.1,relheight=0.05,relwidth = 0.2, anchor = "ne")
name_entry.bind('<Return>', enter_name)

name_button = ttk.Button(root,text="Enter your name",command=enter_name, state="disable")
name_button.place(relx=0.97,rely=0.17,relheight=0.05,relwidth=0.2,anchor="ne")
name_button.bind(enter_name)

credit_button = ttk.Button(root,text="Credit",command=credit)
credit_button.place(relx=0.97,rely=0.9,relheight=0.05,relwidth=0.2,anchor="ne")
credit_button.bind(credit)






# Initial frame 


_, frame = cap.read()
if frame is not None:
	image = convert_to_image(frame)
	photo = ImageTk.PhotoImage(image=image)
	canvas.create_image(WIDTH, HEIGHT, image=photo, anchor="se")


# Start the show


if __name__ == '__main__':
	update_frame()

#create the GUI
root.mainloop()

#free memory
cap.release()
gc.collect()
