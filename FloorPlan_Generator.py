import tkinter
import customtkinter
from CTkMessagebox import CTkMessagebox
from PIL import ImageTk, Image
from screeninfo import get_monitors
import os
import shutil
import pywavefront
import cv2
import math
import numpy as np
import matplotlib.pyplot as plt
import keras_ocr
import threading


def count(n):
    global Counter
    if n == True:
        Counter += 1
    else:
        Counter -= 1
    return Counter

def midpoint(x1, y1, x2, y2):
    x_mid = int((x1 + x2)/2)
    y_mid = int((y1 + y2)/2)
    return (x_mid, y_mid)

def iterator():
    counter = count(True)
    obj_label.configure(image = files_array[counter%len(files_array)])
    #obj_text_label.configure(text = files_name_array[counter%len(files_array)])

def backerator():
    counter = count(False)
    obj_label.configure(image = files_array[counter%len(files_array)])
    #obj_text_label.configure(text = files_name_array[counter%len(files_array)])

def select():
    progess_bar.start()
    progress_label.configure(text = 'GCODE GENERATION IN PROGRESS')
    pipeline = keras_ocr.pipeline.Pipeline()
    gcode = []
    # read image
    img_path = os.listdir('dataset\Images')
    x = img_path[Counter]
    img = keras_ocr.tools.read('dataset\Images\\' + str(x))
    # generate (word, box) tuples
    prediction_groups = pipeline.recognize([img])
    mask = np.zeros(img.shape[:2], dtype="uint8")
    for box in prediction_groups[0]:
        x0, y0 = box[1][0]
        x1, y1 = box[1][1]
        x2, y2 = box[1][2]
        x3, y3 = box[1][3]

        x_mid0, y_mid0 = midpoint(x1, y1, x2, y2)
        x_mid1, y_mi1 = midpoint(x0, y0, x3, y3)

        thickness = int(math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 ))

        cv2.line(mask, (x_mid0, y_mid0), (x_mid1, y_mi1), 255, thickness)
        img = cv2.inpaint(img, mask, 7, cv2.INPAINT_NS)

        plt.imsave('dataset\WithoutText_Images\WT.png', img)

        image = cv2.imread('dataset\WithoutText_Images\WT.png', cv2.IMREAD_GRAYSCALE)

        # Convert the image to binary
        _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

        # Find contours in the binary image
        contours, _ = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        gcode = contours_to_gcode(contours)
        with open("floorplan.gcode", "w") as f:
            for line in gcode:
                f.write(line + "\n")

    progess_bar.stop()
    progess_bar.set(0)
    progress_label.configure(text = '')
    print("G-code generation complete.")
    CTkMessagebox(app, title='info', message='GCODE GENERATION COMPLETED', fg_color = '#705e52', bg_color = '#b19c8f', text_color = 'white', font = customtkinter.CTkFont(family = 'Stencil', size = 20), button_text_color = 'white', button_hover_color = '#29221e', button_color = '#705e52')
    #return(True)



def contours_to_gcode(contours):
    gcode = []
    gcode.append("G21 ; Set units to millimeters")
    gcode.append("G90 ; Absolute positioning")
    gcode.append("G28 ; Home all axes")
    gcode.append("M107 ; Fan off")
    gcode.append("G92 E0 ; Reset extruder position")
    gcode.append("G1 Z5 F5000 ; Lift nozzle")

    extrusion_amount = 10  # 10mm extrusion for each segment
    e_position = 0

    for contour in contours:
        if len(contour) == 0:
            continue
        # Move to the starting point of the contour
        start_point = contour[0][0]
        gcode.append(f"G0 X{start_point[0]} Y{start_point[1]}")
        gcode.append("G1 Z0.3 F1000 ; Lower to the bed")

        # Draw the contour
        for i in range(len(contour)):
            x, y = contour[i][0]
            e_position += extrusion_amount
            gcode.append(f"G1 X{x} Y{y} E{e_position} F1500")

        gcode.append("G1 Z5 F5000 ; Lift the head")

    gcode.append("G28 ; Home all axes")
    gcode.append("M84 ; Disable motors")

    return gcode

def ThreadedSelect():
     threading.Thread(target=select).start()

def screen_resolution():
    for m in get_monitors():
        w = m.width
        h = m.height
    return w,h

   
Counter = 0

customtkinter.set_appearance_mode('system')
customtkinter.set_default_color_theme('green')


app = customtkinter.CTk()

app.geometry('750x780')
app.title('Floor Plan Generator | Vektor Integration')
app.iconbitmap('favicon.ico')
app.minsize(750,780)
app.maxsize(750,900)


background = customtkinter.CTkLabel(app, text = 'Floor Plan Generator', font = ('Vladimir Script', 80), text_color = 'black', bg_color = '#b19c8f', width = 1920, height = 1080, anchor = 'n')
background.pack(fill = 'both')

main_frame = customtkinter.CTkLabel(background, width = 600, height = 660, corner_radius = 30, bg_color = '#b19c8f', fg_color = '#705e52')
main_frame.place(x = 382, y = 430, anchor = tkinter.CENTER)



button1 = customtkinter.CTkButton(app, text = 'NEXT', width = 200, height = 25, font = ('Vladimir Script', 50), text_color = 'white', corner_radius = 30, border_width = 5, border_color = "#b19c8f", bg_color = '#705e52', fg_color = '#705e52', hover_color = '#29221e', command = iterator)
button1.place(x = 552, y = 570, anchor = tkinter.CENTER)

button2 = customtkinter.CTkButton(app, text = 'BACK', width = 200, height = 25, font = ('Vladimir Script', 50), text_color = 'white', corner_radius = 30, border_width = 5, border_color = "#b19c8f", bg_color = '#705e52', fg_color = '#705e52', hover_color = '#29221e', command = backerator)
button2.place(x = 220, y = 570, anchor = tkinter.CENTER)

button3 = customtkinter.CTkButton(app, text = 'SELECT', width = 300, height = 50, font = ('Vladimir Script', 50), text_color = 'white', corner_radius = 30, border_width = 5, border_color = "#b19c8f", bg_color = '#705e52', fg_color = '#705e52', hover_color = '#29221e', command =  ThreadedSelect)
button3.place(x = 380, y = 680, anchor = tkinter.CENTER)


picture_frame = customtkinter.CTkFrame(app, width = 550, height = 400, border_color = '#b19c8f', border_width = 4, bg_color = '#705e52')
picture_frame.place(x = 385, y = 315, anchor = tkinter.CENTER)

files_array = []
files_name_array = []
files = os.listdir('dataset\Images')
for file in files:
    img  = ImageTk.PhotoImage(Image.open(os.path.join('dataset\Images', file)).resize((540,390)))
    file_name = os.path.splitext(file)
    files_array.append(img)
    files_name_array.append(file_name[0])
#for file in obj_files:
    #object_files_array.append(file)     

obj_label = customtkinter.CTkLabel(picture_frame, image = files_array[0], text='')
obj_label.place(relx = 0.5, rely = 0.5, anchor = tkinter.CENTER)

progess_bar  = customtkinter.CTkProgressBar(app, width = 400, corner_radius = 30, fg_color = '#b19c8f', progress_color = '#29221e', indeterminate_speed= 0.5, mode = 'indeterminate')
progess_bar.place(x = 180, y = 745)
progess_bar.set(0)

progress_label = customtkinter.CTkLabel(app, text="", text_color = 'white', font = ('Helvetica', 12), bg_color = '#705e52')
progress_label.place(x = 380, y = 730, anchor = tkinter.CENTER)

#obj_text_label = customtkinter.CTkLabel(app, text = files_name_array[0], text_color = '#AD9655', font = ('Agency FB', 40), height = 50, bg_color = 'black', fg_color = 'black')
#obj_text_label.place(x = 500, y = 450, anchor = tkinter.CENTER)

#company_label = customtkinter.CTkLabel(app, text = '© All Rights Reserved', text_color = '#AD9655', font = ('Times New Roman', 20), height = 50, bg_color = 'black', fg_color = 'black')
#company_label.place(x = 900, y = 700, anchor = tkinter.CENTER)

app.mainloop()



