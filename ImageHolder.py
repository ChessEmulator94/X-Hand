"""
Conttainer Class for XHAND image processing
Contributed to by:
    Lucas Carr      |   CRRLUC003
    Gadi Friedman   |   FRDGAD001
    Gabriel Marcus  |   MRCGAB004

2022-08-08
University of Cape Town
Capstone Project: X-Hand Image Processing
"""


import  numpy as np
import  cv2   as cv


"""
- Class to act as a container to hold ImageObjects
- Has functions to access and mutate the class, as well as relevant parameters 
        Parameters  : void
        Returns     : void                                                          
"""
class ImageHolder:
    
    image_objects         = [] 
    position              = 0
    ideal_image           = np.array(cv.imread("Images/.Hiden/ideal.png", 0))
    ideal_image2          = cv.cvtColor(ideal_image, cv.COLOR_GRAY2BGR)
    #print(ideal_image2.shape)
    ideal_image2[..., 0]  = cv.multiply(ideal_image2[..., 0], 5)
    scale_percent         = 25
    width                 = int(ideal_image.shape[1] * scale_percent / 100)
    height                = int(ideal_image.shape[0] * scale_percent / 100)
    dim                   = (width, height)
    resized               = cv.resize(ideal_image2, dim, interpolation=cv.INTER_AREA)
    ideal_image_resized   = np.array(resized)


    '''
    Adds an ImageObject to the container created for the objects
            Parameters  : ImageObject <ImageObject>
            Returns     : void                                          
    '''
    def addImage(self, ImageObject):

        self.image_objects.append(ImageObject)


    '''
    Returns the container of overall ImageObjects
            Parameters  : 
            Returns     : image_objects <[<ImageObject>]>               
    '''
    def getImageObjects(self):

        return self.image_objects


    '''
    Increments the position by 1
            Parameters  : 
            Returns     : void                                         
    '''
    def incrementPosition(self):

        self.position  += 1
        self.position  %= len(self.image_objects)
    

    '''
    Decrements the position by 1
            Parameters  : 
            Returns     : void                                          
    '''
    def decrementPosition(self):

        self.position  -= 1
        self.position  %= len(self.image_objects)
            

    '''
    Clears the container of all ImageObjects
            Parameters  :   
            Returns     : void                                          
    '''
    def clearContainer(self):

        self.position       = 0
        self.image_objects  = []