'''
GUI for XHAND image processing
'''

from pathlib import Path
import customtkinter as ck
from PIL import ImageTk, Image
import numpy as np
import cv2 as cv
from tkinter import Tk, filedialog
import platform
from ImageHolder import ImageHolder
import xhand

#___________s___ Setting up the Tkinter Frames/Sizes  ________

root = ck.CTk()
w = 1200
h = 800

root.geometry(f"{w}x{h}")
ck.set_appearance_mode("dark") 
ck.set_default_color_theme(".Themes/xhand_theme.json")

frame = ck.CTkFrame(master=root, width=1200, height=800, corner_radius=10)
frame_2 = ck.CTkFrame(master=root, width=1200, height=800, corner_radius=10)
frame.pack(padx=20, pady=20)

original_overlay_bool = ck.BooleanVar(root, False)
ideal_overlay_bool = ck.BooleanVar(root, False)

#####################################
##             Methods             ##
#####################################

#______________ Methods for the 1st Frame  ________

def manageInput():
    try:
        xhand.input_path = filedialog.askdirectory(
            initialdir=str(Path.home() / "Desktop")
        )
        input_path_label.configure(text=xhand.input_path)
    except:
        return

def setOutputPath():
    try:
        root.focus_force()
        xhand.output_path = filedialog.askdirectory(initialdir="Images/Output Images")
        xhand.output_path += "/"
        output_path_label.configure(text=xhand.output_path)
    except:
        return

def callProcessImage():
    if (xhand.input_path == "No input path specified" or xhand.input_path == ""):
        no_valid_path_label.place(relx=0.3, rely=0.8,height=40, width=200)
    else:
        xhand.readInFiles(xhand.input_path)
        loadSecondFrame()
    return

def loadSecondFrame():
    frame.forget()
    frame_2.pack(padx=20, pady=20)
    image = xhand.image_containter.image_objects[xhand.image_containter.position].displayProcessedImage(original_overlay_bool.get(), ideal_overlay_bool.get())
    display_image.configure(image=image)
    display_image.image = image
    getName()
    return

#______________ Methods for the 2nd Frame  ________

def displayImage():
    image = xhand.image_containter.image_objects[xhand.image_containter.position].displayProcessedImage(original_overlay_bool.get(), ideal_overlay_bool.get())
    display_image.configure(image=image)
    display_image.image = image

def nextImage():
    xhand.image_containter.incrementPosition()
    image = xhand.image_containter.image_objects[
        xhand.image_containter.position
    ].displayProcessedImage(original_overlay_bool.get(), ideal_overlay_bool.get())
    display_image.configure(image=image)
    display_image.image = image
    getName()
    return

def previousImage():
    xhand.image_containter.decrementPosition()
    image = xhand.image_containter.image_objects[
        xhand.image_containter.position
    ].displayProcessedImage(original_overlay_bool.get(), ideal_overlay_bool.get())
    display_image.configure(image=image)
    display_image.image = image
    getName()
    return

def getName():
    name = xhand.image_containter.image_objects[
        xhand.image_containter.position
    ].filename
    image_name.configure(text=name)
    image_name.text = name
    return

def back():
    frame_2.forget()
    frame.pack(padx=20, pady=20)
    return

def writeImagesToFile():
    xhand.writeImages(xhand.output_path, xhand.image_containter)
    confirmation_write.place(relx=0.2, rely=0.295)
    return


#####################################
##         Buttons/Labels          ##
#####################################

#______________ Dummy Image for Image Viewer  _____________


dummy_image = ImageTk.PhotoImage(image=Image.fromarray(ImageHolder.ideal_image_resized))

#______________ Labels/Buttons for the 1st Frame  ________
header_label = ck.CTkLabel(
    master=frame,
    text="XHAND Image Preprocessing",
    width=500,
    height=50,
    fg_color="#292929",
    text_color="#c6c9c3",
    corner_radius=8)
header_label.configure(font=("Roboto 36 bold"))
header_label.place(relx=0.18, rely=0.2)

select_inputs_button = ck.CTkButton(
    master=frame, 
    text="Choose Input Directory", 
    command=manageInput)
select_inputs_button.place(relx=0.1, rely=0.6, height=40, width=200)

input_path_label = ck.CTkLabel(
    master=frame,
    text=xhand.input_path,
    width=400,
    height=40,
    fg_color="#292929",
    text_color="#c6c9c3",
    anchor="w",
    corner_radius=8)
input_path_label.place(relx=0.3, rely=0.6)

no_valid_path_label = ck.CTkLabel(
    master=frame,
    text="Invalid path! Try again.",
    width=400,
    height=400,
    fg_color="#292929",
    text_color="#c6c9c3",
    anchor="w",
    corner_radius=8)

select_outputs_button = ck.CTkButton(
    master=frame, 
    text="Choose Output Directory", 
    command=setOutputPath)
select_outputs_button.place(relx=0.1, rely=0.7, height=40, width=200)

output_path_label = ck.CTkLabel(
    master=frame,
    text=xhand.output_path,
    width=400,
    height=40,
    fg_color="#292929",
    text_color="#c6c9c3",
    anchor="w",
    corner_radius=8)
output_path_label.place(relx=0.3, rely=0.7)

process_images_button = ck.CTkButton(
    master=frame, 
    text="Process Images", 
    command=callProcessImage)
process_images_button.place(relx=0.1, rely=0.8, height=40, width=200)

#______________ Labels/Buttons for the 2nd Frame  ________
back_button = ck.CTkButton(master=frame_2, 
    text="Back", 
    command=back)
back_button.place(relx=0.025, rely=0.05, height=40, width=100)

exit_button = ck.CTkButton(master=root, 
    text="Quit", 
    command=root.destroy)
exit_button.place(relx=0.875, rely=0.05, height=40, width=100)

display_image = ck.CTkLabel(
    master=frame_2, 
    image=dummy_image, 
    height=500, 
    bg_color="black", 
    width=375)
display_image.place(relx=0.6, rely=0.2)

next_button = ck.CTkButton(
    master=frame_2, 
    text=">", 
    height=40, 
    width=40, 
    command=nextImage)
next_button.place(relx=0.89, rely=0.87)

prev_button = ck.CTkButton(
    master=frame_2, 
    text="<", 
    height=40, 
    width=40, 
    command=previousImage)
prev_button.place(relx=0.6, rely=0.87)

image_name = ck.CTkLabel(
    master=frame_2,
    text="default.png",
    height=40,
    width=40,
    fg_color="#292929",
    text_color="#c6c9c3",)
image_name.place(relx=0.7, rely=0.87)
image_name.configure(font=("Roboto 18"))

preview_options_label = ck.CTkLabel(master=frame_2,
    text="Preview Options",
    fg_color="#292929",
    text_color="#c6c9c3",
    corner_radius=8)
preview_options_label.configure(font=("Roboto 28 bold"))
preview_options_label.place(relx=0.35, rely=0.2)

original_image_checkbox = ck.CTkCheckBox(master=frame_2, 
    text="Compare to original image", 
    fg_color="#292929",
    text_color="#c6c9c3", 
    command=displayImage,
    variable=original_overlay_bool, 
    onvalue="on", 
    offvalue="off")
original_image_checkbox.place(relx=0.36, rely=0.3)

ideal_image_checkbox = ck.CTkCheckBox(master=frame_2, 
    text="Compare to 'ideal' image",    
    fg_color="#292929",
    text_color="#c6c9c3", 
    command=displayImage,
    variable=ideal_overlay_bool, 
    onvalue="on", 
    offvalue="off")
ideal_image_checkbox.place(relx=0.36, rely=0.375)

functions_label = ck.CTkLabel(master=frame_2,
    text="Functions",
    fg_color="#292929",
    text_color="#c6c9c3",
    corner_radius=8)
functions_label.configure(font=("Roboto 28 bold"))
functions_label.place(relx=0.065, rely=0.2)

write_images_button = ck.CTkButton(
    master=frame_2, 
    text="Write Images", 
    command=writeImagesToFile)
write_images_button.place(relx=0.067, rely=0.3, height=30, width=150)

confirmation_write = ck.CTkLabel(
    master=frame_2,
    text="Success!",
    width=100,
    height=40,
    fg_color="#292929",
    text_color="#c6c9c3",
    corner_radius=8)
confirmation_write.configure(font=("Roboto 14"))

find_similar_button = ck.CTkButton(
    master=frame_2, 
    text="Find Similar Hands", 
    command=writeImagesToFile)
find_similar_button.place(relx=0.067, rely=0.375, height=30, width=150)

confirmation_write = ck.CTkLabel(
    master=frame_2,
    text="Success!",
    width=100,
    height=40,
    fg_color="#292929",
    text_color="#c6c9c3",
    corner_radius=8)
confirmation_write.configure(font=("Roboto 14"))


#   Temporary (FOR DEMO ONLY)
# ________________________________________________
confirmation_process = ck.CTkLabel(
    master=frame_2,
    text="Images have been processed.",
    width=100,
    height=40,
    fg_color="#292929",
    text_color="#c6c9c3",
    corner_radius=8,
)
confirmation_process.configure(font=("Roboto 18"))
confirmation_process.place(relx=0.1, rely=0.7)


# _________________________________________________

root.mainloop()
