

import  os
import  sys
import  tkinter as tk
from    pathlib import Path
from    tkinter import filedialog
import  customtkinter as ck
import  Pmw
from    PIL import Image, ImageTk
import  xhand

text_colour    = "#212121"
dark_text      = "#F5EFE6"
button_colour  = "#6D9886"
bgcolor        = "#212121"


'''
Class for the initial interface the user interacts with
'''
class Screen1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent,  bg=bgcolor)


        '''
        Receives and updates the input path in xhand
                Parameters  : 
                Returns     :  void 
        '''
        def manageInput():
            
            try:
                xhand.input_path = filedialog.askdirectory(initialdir=str(Path.home() / "Desktop"))
                input_path_label.configure(text=xhand.input_path)

            except:

                return


        '''
        Receives and updates the output path in xhand
            Parameters  : 
            Returns     :  void
        '''
        def setOutputPath():
            
            try:
                self.focus_force()
                xhand.output_path  = filedialog.askdirectory(initialdir = "Images/Output Images")
                xhand.output_path  += "/"
                output_path_label.configure(text=xhand.output_path)
                print(xhand.output_path)

            except:

                return


        '''
        Checks to see if valid input path, if valid then begins image processing 
        and moves to 2nd screen 
                Parameters  : 
                Returns     :  void
        '''
        def callProcessImage():
            if xhand.input_path == "No input path specified" or xhand.input_path == "":
                no_valid_path_label.configure(text = "No input directory given.")
                no_valid_path_label.place(relx = 0.4, rely = 0.8, height = 40, width = 400)

            elif not any(fname.endswith('.png') for fname in os.listdir(xhand.input_path)):
                no_valid_path_label.configure(text = "Directory does not contain any '.png' files.")
                no_valid_path_label.place(relx = 0.4, rely = 0.8, height = 40, width = 400)

            else:
                xhand.readInFiles(xhand.input_path)
                loadSecondFrame()
            
            return


        '''
        Helper to move to second screen
            Parameters  : 
            Returns     :  void
        '''
        def loadSecondFrame():
            
            controller.show_frame(Screen2)

            return


        header_label = ck.CTkLabel(
            self,
            text           = "XHAND Image Preprocessing",
            width          = 500,
            height         = 50,
            text_color     = dark_text,
            corner_radius  = 8,
        )

        header_label.configure(font = ("Roboto 56 bold"))
        header_label.place(relx = 0.2, rely = 0.2)

        select_inputs_button = ck.CTkButton(
            self,
            text        = "Choose Input Directory",
            text_color  = text_colour,
            fg_color    = button_colour,
            command     = manageInput,
        )

        select_inputs_button.place(relx = 0.2, rely = 0.6, height = 40, width = 200)
        input_path_label = ck.CTkLabel( 
            self,
            text          = xhand.input_path,
            width         = 400,
            height        = 40,
            text_color    = dark_text,
            anchor        = "w",
            corner_radius = 8,
        )
        input_path_label.place(relx = 0.4, rely= 0.6)

        no_valid_path_label = ck.CTkLabel(
            self,
            text           = "Invalid path! Try again.",
            width          = 400,
            height         = 400,
            text_color     = dark_text,
            anchor         = "w",
            corner_radius  = 8,
        )

        select_outputs_button = ck.CTkButton(
            self,
            text     =  "Choose Output Directory",
            fg_color =  button_colour,
            command  =  setOutputPath,
        )
        select_outputs_button.place(relx = 0.2, rely = 0.7, height= 40, width = 200)

        output_path_label = ck.CTkLabel(
            self,
            text           = xhand.output_path,
            width          = 400,
            height         = 40,
            text_color     = dark_text,
            anchor         = "w",
            corner_radius  = 8,
        )
        output_path_label.place(relx = 0.4, rely = 0.7)

        process_images_button = ck.CTkButton(
            self,
            text      = "Process Images",
            fg_color  = button_colour,
            command   = callProcessImage,
        )
        process_images_button.place(relx = 0.2, rely = 0.8, height = 40, width = 200)


'''
Class for the second interface the user interacts with 
'''
class Screen2(tk.Frame):
    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent, bg=bgcolor)
        original_overlay_bool   = ck.BooleanVar(self, False)
        ideal_overlay_bool      = ck.BooleanVar(self, False)
        dummy_image             = ImageTk.PhotoImage(
            image=Image.fromarray(xhand.image_containter.ideal_image_resized)
        )


        '''
        Displays an image from the container on the preview window 
                Parameters  :
                Returns     :  void
        '''
        def displayImage():
            
            image  = xhand.image_containter.image_objects[
                xhand.image_containter.position
            ].displayProcessedImage(
                original_overlay_bool.get(), ideal_overlay_bool.get()
            )
            display_image.configure(image=image)
            display_image.image  = image

        prev_button  = ck.CTkButton(
            self, text  = "display images", height = 40, width = 40, command = displayImage)
        prev_button.place(relx = 0.3, rely = 0.8)


        '''
        Displays the next image in the container 
                Parameters  : 
                Returns     :  void
        '''
        def nextImage():
            
            xhand.image_containter.incrementPosition()
            image  =  xhand.image_containter.image_objects[
                xhand.image_containter.position
            ].displayProcessedImage(original_overlay_bool.get(), ideal_overlay_bool.get())
            display_image.configure(image = image)
            display_image.image  =  image
            getName()

            return


        '''
        Displays the previous image in the container
                Parameters  :
                Returns     :  void
        '''
        def previousImage():
            
            xhand.image_containter.decrementPosition()
            image  =  xhand.image_containter.image_objects[
                xhand.image_containter.position
            ].displayProcessedImage(
                original_overlay_bool.get(), ideal_overlay_bool.get()
            )
            display_image.configure(image=image)
            display_image.image  =  image
            getName()
            
            return


        '''
        Displays the current image name  
                Parameters  : 
                Returns     :  void
        '''
        def getName():
            
            name = xhand.image_containter.image_objects[
                xhand.image_containter.position
            ].filename
            image_name.configure(text=name)
            image_name.text = name

            return

        '''
        Returns to the previous screen. 
            Parameters  : 
            Returns     :  void  
        '''
        def back():
            
            xhand.image_containter.clearContainer()
            controller.show_frame(Screen1)
            
            return
        

        '''
        Calls the clustering function
                Parameters  :
                Returns     :  void  
        '''
        def clusteringFunctionGUI():
           
            xhand.computeGroupsBD(int (num_clusters.get()))
            return
        

        '''
        Calls the clustering function
                Parameters  :
                Returns     :  void  
        '''
        def findCenter():
            
            available_choices = (("bone density", -1), ("index finger",1),  ("middle finger", 2))
            choice_index = -1
            for val, tup in enumerate(available_choices): 
                if tup[0] == options.get():
                    choice_index = val
                    
            corresponding_choice_value  = int(available_choices[choice_index][1])
            standard_deviation          = int(deviations.get())
            print(corresponding_choice_value, "\n", standard_deviation)
            xhand.findCenterOfDist(corresponding_choice_value, standard_deviation)
            
            return


        '''
        Calls the function that finds similar hands
                Parameters  :
                Returns     :  void  
        '''
        def find_similar(): 
            
            comparison_hand = xhand.image_containter.image_objects[xhand.image_containter.position]
            available_choices = (("bone density", 0), ("index finger",1),  ("middle finger", 2))
            choice_index = 0
            for val, tup in enumerate(available_choices): 
                if tup[0] == options.get():
                    choice_index = val

            list_comparitor = []
            for hand in xhand.image_containter.image_objects:

                if choice_index == 0:
                    item  = (hand, hand.bone_percentage)
                
                elif choice_index == 1:
                    item  = (hand, hand.finger_lengths[1])
                
                else:
                    item  = (hand, hand.finger_lengths[2]) 

                list_comparitor.append(item)

            xhand.findSimilarHands(comparison_hand, list_comparitor)
        
        
        '''
        Calls the function in xhand to write images from container to storage
                Parameters  : 
                Returns     :  void
        '''
        def writeImagesToFile():
            
            xhand.writeImages(xhand.output_path, xhand.image_containter)
            confirmation_write.place(relx = 0.375, rely = 0.71)
            
            return

        back_button = ck.CTkButton(
            self, text="Back", fg_color=button_colour, command=back
        )
        back_button.place(relx = 0.025, rely = 0.05, height = 40, width = 100)

        exit_button = ck.CTkButton(
            self, text="Quit", fg_color=button_colour, command=lambda: sys.exit(0)
        )

        exit_button.place(relx = 0.875, rely = 0.05, height = 40, width = 100)
        
        display_image = ck.CTkLabel(
            self,
            image     = dummy_image,
            height    = 500,
            bg_color  = "black",
        )

        display_image.configure(image=dummy_image)
        display_image.image = dummy_image
        display_image.place(relx = 0.6, rely = 0.2, width = 392)

        next_button = ck.CTkButton(
            self,
            text      = ">",
            height    = 40,
            width     = 40,
            fg_color  = button_colour,
            command   = nextImage,
        )

        next_button.place(relx = 0.89, rely = 0.83)
        prev_button  = ck.CTkButton(

            self,
            text      = "<",
            height    = 40,
            width     = 40,
            fg_color  = button_colour,
            command   = previousImage,
        )
        prev_button.place(relx = 0.6, rely = 0.83)

        image_name = ck.CTkLabel(
            self,
            text        = "default.png",
            height      = 40,
            width       = 40,
            text_color  = "#c6c9c3",
        )

        image_name.place(relx = 0.7, rely = 0.83)
        image_name.configure(font = ("Roboto 18"))

        preview_options_label  = ck.CTkLabel(
            self, text="Preview Options", text_color=dark_text, corner_radius=8
        )
        preview_options_label.configure(font = ("Roboto 28 bold"))
        preview_options_label.place(relx = 0.35, rely = 0.2)

        original_image_checkbox = ck.CTkCheckBox(
            self,
            text        = "Compare to original image",
            fg_color    = button_colour,
            text_color  = dark_text,
            command     = displayImage,
            variable    = original_overlay_bool,
            onvalue     = "on",
            offvalue    = "off",
        )
        original_image_checkbox.place(relx = 0.36, rely = 0.3)

        ideal_image_checkbox = ck.CTkCheckBox(
            self,
            text        = "Compare to 'ideal' image",
            fg_color    = button_colour,
            text_color  = dark_text,
            command     = displayImage,
            variable    = ideal_overlay_bool,
            onvalue     = "on",
            offvalue    = "off",
        )
        ideal_image_checkbox.place(relx = 0.36, rely = 0.375)

        functions_label  = ck.CTkLabel(
            self, text="Functions", text_color=dark_text, corner_radius=8
        )
        functions_label.configure(font = ("Roboto 28 bold"))
        functions_label.place(relx = 0.065, rely = 0.2)

        write_images_button  = ck.CTkButton(
            self, text="Write Images", fg_color=button_colour, command=writeImagesToFile
        )
        write_images_button.place(relx = 0.2, rely = 0.7, height = 60, width = 200)

        confirmation_write = ck.CTkLabel(
            self,
            text="Success!",
            width=100,
            height=40,
            text_color=dark_text,
            corner_radius=8,
        )
        confirmation_write.configure(font=("Roboto 14"))

        clustering_button = ck.CTkButton(
            self,
            text="Cluster Images",
            fg_color=button_colour,
            command=clusteringFunctionGUI,
        )
        num_clusters = tk.StringVar(self)
        num_clusters.set("3")

        cluster_option_select = tk.OptionMenu(self, num_clusters, "1","2", "3", "4", "5", "6", "7")
        cluster_option_select.config(bg = "#212121", fg = "white", borderwidth = 0)
        cluster_option_select.place(relx = 0.21,rely = 0.3, height = 30, width = 100)
        clustering_button.place(relx = 0.067, rely = 0.3, height = 30, width = 150)
        clustering_tooltip = Pmw.Balloon(self) #Calling the tooltip
        clustering_tooltip.bind(clustering_button,'Performs K means clustering based on the selected amount of clusters. Clustering is performed based on the bone density of hands.') 

        findCenterButton = ck.CTkButton(
            self,
            text      = "Find center",
            fg_color  = button_colour,
            command   = findCenter,
        )

        options = tk.StringVar(self)
        options.set("bone density") # default value
        findCenterButton.place(relx = 0.067, rely = 0.375, height = 30, width = 150)
        findCenter_options = tk.OptionMenu(self, options, "bone density","index finger", "middle finger")
        findCenter_options.config(bg = "#212121", fg = "white", borderwidth = 0)
        findCenter_options['menu'].config(bg='#242B2D')
        findCenter_options.place(relx = 0.21,rely = 0.377, height = 20, width = 90)
        find_center_tooltip = Pmw.Balloon(self) #Calling the tooltip
        find_center_tooltip.bind(findCenterButton,'Finds all hands that are within the chosen amount of Standard Deviations from the mean. Parameter used to determine spread of data is selected by user.') 

        deviations = tk.StringVar(self)
        deviations.set("1") # default value
        standard_deviation_select = tk.OptionMenu(self, deviations, "1","2", "3", "4", "5", "6", "7")
        standard_deviation_select.config(bg = "#212121", fg = "white", borderwidth = 0)
        standard_deviation_select.place(relx = 0.3,rely = 0.373, height = 30, width = 45)
        standard_deviation_tooltip = Pmw.Balloon(self) 
        standard_deviation_tooltip.bind(self,'This is the tooltip for the clustering button. \n There should be more text here, ask Gadi.') 

        find_similar_button = ck.CTkButton(
            self,
            text      = "Find Similar",
            fg_color  = button_colour,
            command   = find_similar,
        )

        similar_options = tk.StringVar(self)
        similar_options.set("bone density") # default value
        find_similar_button.place(relx = 0.067, rely = 0.450, height = 30, width = 150)
        findSimilar_options = tk.OptionMenu(self, options, "bone density","index finger", "middle finger")
        findSimilar_options.config(bg = "#212121", fg = "white", borderwidth = 0)
        findSimilar_options['menu'].config(bg='#242B2D')
        findSimilar_options.place(relx = 0.21,rely = 0.452, height = 20, width = 90)

        find_similar_tooltip = Pmw.Balloon(self) #Calling the tooltip
        find_similar_tooltip.bind(find_similar_button,'Computes a disimalirity matrix of all hands based on user chosen parameter. Saves all hands that are similar to the currently displayed image.') 
        
