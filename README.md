# **Capstone Project: XHAND**
Contributers
: Lucas Carr, Gadi Friedman, Gabriel Marcus  <br> 


## **Installation**
All the required python libraries are listed in _requirements.txt_; you can easily install these by using the command : `make install`, use `make clean` to uninstall if necessary.  <br>  

    *! if you encounter an error similar to 'python not configured for Tk', 
    the solution for this is to manually install Tkinter. Use your package manager 
    (pacman/homebrew/paru), e.g. sudo pacman -S tk
    
    This is the result of a known buggy interaction between TKinter and virtual environments.


After this, to enter the virtual environment, use: `source venv/bin/activate`

The software is now ready!  

<br>  
<hr />
<br>  

## **Running the Software**
You will need to have: 
1. A batch of `.png` images stored in a directory you have access to. 
2. Space on your drive to write images to (if you wish to write the processed images to file)

### **Selecting input path**
- Use the buttons on the interface to select the directory containing your images. 

- Next, specify the folder where you would like to write the processed images to ___(this step is optional, if you choose not to specify an output directory, the default directory will be used - this is `xhand/Images/Output Images/`)___. 

- After processing the images, the interface will show you the second screen. Here, you should see a preview of the processed image ___(you can navigate between images using the arrow keys)___. 

- By default, the final output image is previewed; you may use the check-boxes to select if you would to view image overlays ___(the options are explained on the check-boxes)___.  


<br>  
<hr />
<br>  

## **Classes**
There are 4 classes present: 

- __xhand.py__  
    Acts as the driver class for the program. Member functions provide functionality for reading/writing images, as well processing images. 

- __gui.py__    
    Reponsible for providing the interface to the user. Member functions act as ports which call functions from _xhand.py_

- __ImageObject.py__    
    Class which holds image objects, which contain source image, processed image, and a filename. 

- __ImageHolder.py__    
    Class which holds image objects, which contain source image, processed image, and a filename. 