"""
GUI for XHAND image processing
Contributed to by:
    Lucas Carr      |   CRRLUC003
    Gadi Friedman   |   FRDGAD001
    Gabriel Marcus  |   MRCGAB004

2022-08-08
University of Cape Town
Capstone Project: X-Hand Image Processing
"""


import  numpy as np
import  cv2 as cv
import  math
from    ImageHolder import ImageHolder
from    PIL import ImageTk, Image


"""
- Stores information about individual images
- Has functions that perform various processes on images 
        Parameters  : void
        Returns     : void                                                          
"""
class ImageObject:

# Various types of processing are applied to the source image. These various images
# are stored in the below arrays

    # To hold image with noise removed  
    image_original            = np.array(0)
    # To hold image with noise removed and rotation applied
    image_rotated           = np.array(0)
    # To hold a single image composed of original and image_rotated (overlayed) 
    overlayed_images_basic  = np.array(0)
    # To hold a single image composed of "ideal image" and image_rotated (overlayed)
    overlayed_images_ideal  = np.array(0)
    # To hold a single image composed of "ideal image",image_rotated, and image_original (overlayed)
    overlayed_images_all    = np.array(0)
    # To hold cleaned image that shows primarily bones within the hand
    image_boney             = np.array(0)
    # To hold image used during processing
    image_processed         = np.array(0)

    # Stores the values of finger lengths
    # [1] Index Finger , [2] Middle Finger , [3] Ring Finger
    finger_lengths = []

    # Stores contours between fingers
    contours       = []
    
    # Stores the file name of the original image's location
    filename         = ""
    # Stores the rotation degrees needed to align the image to the vertical (Y) axis
    rotation_factor  = ""
    # Stores the percentage of the total hand that is bone
    bone_percentage  = 0
    # Stores additional relevant info about the hand
    property_concaves  = []
    property_fingers   = []

    finger_property_vector = np.array(0)
    full_hand_mask         = np.array(0)


    """
    Constructor for ImageObject
        Parameters  : image_original <numpy array>, filename <String>
        Returns     : void                                           
    """
    def __init__(self, image_original, filename):

        # Sets basic parameters
        self.image_original  =  image_original
        self.filename        =  filename

        # Performs processing and stores output
        self.image_processed =  self.performProcessing(image_original)

        # Performs rotation and stores output
        self.image_rotated   =  self.computeRotation(self.image_original)

        # Create and store overlay images for rotation visualistion 
        self.image_original[..., 2]  =  cv.multiply(self.image_original[..., 2], 5)
        self.overlayed_images_basic  =  self.overlayImages(self.image_rotated, self.image_original)
        self.overlayed_images_ideal  =  self.overlayImages(self.image_rotated, ImageHolder.ideal_image2)
        self.overlayed_images_all    =  self.overlayImages(self.overlayed_images_basic, ImageHolder.ideal_image2)

        # Computes lenghts of the index, middle and ring fingers
        self.finger_lengths =[]
        for i in range(1, 4):
            concave_pair = []
            concave_pair.append(self.property_concaves[i - 1])
            concave_pair.append(self.property_concaves[i])
            self.finger_lengths.append(self.computeFingerLength(self.property_fingers[i], concave_pair))


    """
    Acts as a driver function, which calls all the image processing functions
        Parameters  : image_original <numpy array>
        Returns     : void                                                 
    """
    def performProcessing(self, image_original):
       
        # Calls functions to perform various processing on images
        default              =   image_original
        image_normalized     =   self.histogramNormalization(image_original)
        image_thresholded    =   self.thresholdImage(image_normalized, True, "b")
        self.image_boney     =   self.thresholdImage(image_normalized, False, "a")
        image_thresholded    =   self.removeBorders(image_thresholded)
        image_cleaned        =   self.cleanImage(image_thresholded)
        cc_analized_image    =   self.ccAnalysis(image_cleaned)
        self.full_hand_mask  =   cc_analized_image
        contoured_image      =   self.findContours(cc_analized_image, default)
        self.image_boney     =   self.computeBoneDensity(self.image_boney)
        image_rotated        =   self.computeRotation(contoured_image)

        return


    """
        Description
        Parameters  : fingertip_points <tuple>, concave_points <tuple>
        Returns     : finger_length<real>                                             
    """
    # concave_points : item[0] is X co-ord, item[1] is Y co-ord 
    # fingertip_points : item[0] is X co-ord, item[1] is Y co-ord 
    def computeFingerLength(self, fingertip_points, concave_points):

        # Calculate length of fingers
        finger_base     = self.midPoint(concave_points[0], concave_points[1])
        finger_value_X  = fingertip_points[0]
        finger_value_Y  = fingertip_points[1]
        finger_tuple    = [finger_value_X, finger_value_Y]
        finger_length   = math.dist(finger_tuple, finger_base)

        return finger_length


    """
    Calculates the percentage of the hand in the image that is bone 
        Parameters  : image_boney <numpy array>
        Returns     : image_boney <numpy array>                                        
    """
    def computeBoneDensity(self, image_boney):
        
        image_boney           = self.maskImage(255, [255] * 3, self.contours, self.image_boney)
        number_of_black_pix   = np.sum(image_boney == 0)
        number_of_white_pix   = np.sum(self.full_hand_mask == 255)
        self.bone_percentage  = number_of_black_pix / number_of_white_pix
        return image_boney


    """
    Performs histogram normalization on image 
            Parameters  : image_original <numpy array>
            Returns     : blur <numpy array>                                        
    """
    def histogramNormalization(self, image_original):
        
        clahe  = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        norm   = clahe.apply(image_original)
        blur   = cv.GaussianBlur(norm, (5, 5), 0)

        return blur


    """
    Performs binary thresholding on image 
            Parameters  : image_normalized <numpy array>, primary <boolean>, thresholding_type <String>
            Returns     : thresh <numpy array>                                      
    """
    def thresholdImage(self, image_normalized, primary, thresholding_type):
        
        #  primary is True when normal full processing is to be applied
        if primary:
            threshold_amount = 25
        #  primary is False for processing to get bone density
        else:
            # must be:  threshold_amount%2 == 1
            # 21 is used to try isolate bones as much as possible
            threshold_amount = 21

        kernel  = np.ones((5, 5), np.uint8)
        closing = cv.morphologyEx(image_normalized, cv.MORPH_CLOSE, kernel)

        # thresholding_type == b for binary thresholding
        if thresholding_type == "b":
            ret, thresh = cv.threshold(closing, threshold_amount, 255, cv.THRESH_BINARY)
        # thresholding_type == a for adaptive thresholding
        else:
            thresh      = cv.adaptiveThreshold(
                closing, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, threshold_amount, 2)

        return np.array(thresh)


    """
    Removes borders around the image for connected component analysis step
            Parameters  : imageObj <numpy array>
            Returns     : void                                                      
    """
    def removeBorders(self, imageObj):

        # Removes border from noise at top of image
        def removeTB():

            width          = imageObj.shape[1]
            start_point_x  = width // 4
            found          = False
            y_left_value   = 0

            # Find first black pixel based on left of image
            while not found:
                colour = imageObj[y_left_value, start_point_x]
                if colour == 0:
                    found   = True
                else:
                    y_left_value += 1

            # Reset parameters
            found          = False
            start_point_x  = width // 4 * 3
            y_right_value  = 0

            # Find first black pixel based on right of image
            while not found:
                colour = imageObj[y_right_value, start_point_x]
                if colour == 0:
                    found = True
                else:
                    y_right_value += 1

            # Determine which side has the lowest touching point on border
            if y_left_value > y_right_value:
                y_value = y_left_value
            else:
                y_value = y_right_value

            # Cut border based on lowest touching point
            imageObj[0:y_value, 0:width] = 0
            return

        # Removes border from noise at bottom of image       
        def removeBB():

            width          = imageObj.shape[1]
            start_point_x  = width // 4
            found          = False
            y_left_value   = imageObj.shape[0] - 1

            # Find first black pixel based on left of image
            while not found:
                colour = imageObj[y_left_value, start_point_x]
                if colour == 0:
                    found = True
                else:
                    y_left_value -= 1

            # Reset parameters
            found          = False
            start_point_x  = width // 4 * 3
            y_right_value  = imageObj.shape[0] - 1

            # Find first black pixel based on right of image
            while not found:
                colour = imageObj[y_right_value, start_point_x]
                if colour == 0:
                    found = True
                else:
                    y_right_value -= 1

            # Determine which side has the lowest touching point on border
            if y_left_value > y_right_value:
                y_value = y_left_value
            else:
                y_value = y_right_value

            # Cut border based on lowest touching point
            imageObj[y_value : imageObj.shape[0] - 1, 0:width] = 0

            return

        # Removes the right hand side noise border if present
        def removeRB():

                height          = imageObj.shape[0]
                start_point_y  = height // 4
                found          = False
                x_bot_value    = imageObj.shape[1] - 1

                # Find first black pixel based on top quarter of image
                while not found:
                    colour = imageObj[start_point_y, x_bot_value]
                    if colour == 0:
                        found = True
                    else:
                        x_bot_value -= 1

                # Reset parameters
                found          = False
                start_point_y  = height // 4 * 3
                x_top_value    = imageObj.shape[1] - 1

                # Find first black pixel based on bottom quarter of image
                while not found:
                    colour = imageObj[start_point_y,x_top_value]
                    if colour == 0:
                        found = True
                    else:
                        x_top_value -= 1

                # Determine which side has the lowest touching point on border
                if x_top_value > x_bot_value:
                    x_value = x_top_value
                else:
                    x_value = x_bot_value

                # Cut border based on lowest touching point
                imageObj[0:height, x_value: imageObj.shape[1]-1] = 0

                return        



        
        # Call the functions to remove the borders
        removeTB()
        removeBB()
        removeRB()

        return imageObj

    """
    Function which, for a given pixel [i][j], will determine whether this pixel should be 0 or 255 based 
    of surrounding area of pixels
            Parameters  : i <int>, j <int>, img <numpy array>
            Returns     : value <int>                                               
    """
    def getWindowAverage(self, i, j, img):
        
        # Get width of image
        image_width = img.shape[1]
        sum         = 0

        if j < (image_width // 2):
            for a in range(2):
                for b in range(3):
                    sum += img[i - b][j + a]
        else:
            for a in range(2):
                for b in range(3):
                    sum += img[i - b][j - a]

        # Returns 255, indicating white
        if sum / 6 > 130:
            return 255

        # Returns 0, indicating black
        return 0


    """
    Function used to call getWindowAverage for a selected number of pixels; 
    ad hoc solution to only do bottom 1/5th of image, since seems to be onlyeffected area.
        Parameters  : img <numpy array>
        Returns     : img <numpy array>                                             
    """
    def cleanImage(self, img):

        # Find image height and width
        image_height  = img.shape[0]
        image_width   = img.shape[1]

        # Create an image with the pixels averaged using getWindowAverage
        for i in range(image_height - round(image_height * 0.1), image_height):
            for j in range(image_width):
                img[i][j] = self.getWindowAverage(i, j, img)

        return img


    """
    Performs connected component analysis on thresholded image  
        Parameters  : image_thresholded <numpy array>
        Returns     : cc_analized_image <numpy array>                               
    """
    def ccAnalysis(self, image_thresholded):
        
        max         = []
        id          = 0
        analysis    = cv.connectedComponentsWithStats(image_thresholded, 4, cv.CV_32S)
        output      = np.zeros(image_thresholded.shape, dtype="uint8")

        (totalLabels, label_ids, values, centroid) = analysis

        for i in range(0, totalLabels):
            max.append(values[i, cv.CC_STAT_AREA])
        max.sort()

        for i in range(0, totalLabels):
            if values[i, cv.CC_STAT_AREA] == max[totalLabels - 2]:
                id = i
        
        componentMask      = (label_ids == id).astype("uint8") * 255
        cc_analized_image  = cv.bitwise_or(output, componentMask)  
        
        return cc_analized_image


    """
    Finds the contours of the component, these contours are then used to find the
    defects, convex hull and fingertips, as well as create the mask around the hand image. 
        Parameters  : threshed_image <numpy array>
        Returns     : img <numpy array>                                             
    """
    def findContours(self, threshed_image, default):

        # Stores the concaves between fingers
        concave_points  = []
        start_points    = []
        end_points      = []
        hand_points     = []

        contours, hierarchy  = cv.findContours(threshed_image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        contours             = max(contours, key=lambda x: cv.contourArea(x))
        self.contours        = contours
        contours2            = map(np.squeeze, contours)

        img = np.zeros([threshed_image.shape[0], threshed_image.shape[1], 3], dtype=np.uint8)
        img[:] = 0

        # Draws the hand contour
        cv.drawContours(img, [contours], -1, (255, 0, 0), 2)
        self.image_original  = self.maskImage(255, [0] * 3, contours, self.image_original)

        # Finds and draws the convexity hull
        hull                 = cv.convexHull(contours)
        cv.drawContours(img, [hull], -1, (0, 255, 255), 2)

        # Find and draws the convexity defects
        hull = cv.convexHull(contours, returnPoints=False)
        defects = cv.convexityDefects(contours, hull)

        # Calculate the angle between points of interest
        for count, i in enumerate(range(defects.shape[0])):
            s, e, f, d  = defects[i][0]
            start       = tuple(contours[s][0])
            end         = tuple(contours[e][0])
            far         = tuple(contours[f][0])
            a           = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b           = np.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c           = np.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
            angle       = np.arccos((b**2 + c**2 - a**2) / (2 * b * c))  

            # If angle is less than 90 degrees, treat as fingers
            if angle <= np.pi / 2:  
                concave_points.append(far)
                start_points.append(start)
                end_points.append(end)

            elif angle > (2.5):
                if np.abs(start[0] - far[0]) > 50:
                    hand_points.append(far)

        # Store calculated hand data points of interest
        self.property_concaves  = concave_points
        self.property_fingers   = self.computeFingertips(start_points, end_points)

        # Draws points of interest onto image (primarily needed for testing)
        for element in concave_points:
            cv.circle(img, element, 10, [255, 0, 0], -1)
        for element in hand_points:
            cv.circle(img, element, 10, [0, 255, 0], -1)
        for element in self.property_fingers:
            cv.circle(img, element, 10, [0, 0, 255], -1)
        
        return img


    """
    Creates a mask around the hand component of image, isolating it
        Parameters  : mask_values <int>, fill_color <[<int>, <int>, <int>]>, contours <[tuple]>, 
                      image <numpy array> 
        Returns     : image <numpy array>                                           
    """
    def maskImage(self, mask_values, fill_color, contours, image):
        
        image       = cv.cvtColor(image, cv.COLOR_BAYER_BG2BGR)
        # Creates the mask to isolate the hand component of image
        stencil     = np.zeros(image.shape[:-1]).astype(np.uint8)

        cv.fillPoly(stencil, np.array([contours], dtype="int32"), mask_values)

        sel         = stencil != mask_values
        # Fills all values not in the mask with fill_color
        image[sel]  = fill_color

        return image


    """
    Calculates the mid point between two co-ordinates  
        Parameters  : a <(<int>, <int>)>, b <(<int>, <int>)>
        Returns     : <(<int>, <int>)>                                              
    """
    def midPoint(self, a, b):

        return (np.abs((a[0] + b[0]) // 2), np.abs((a[1] + b[1]) // 2))


    """
    Finds the fingertips and appends them to an array   
        Parameters  : start_pts <[(<int>, <int>)]>, end_pts <[(<int>, <int>)]>
        Returns     : fingertip_list <[(<int>, <int>)]>                             
    """
    def computeFingertips(self, start_pts, end_pts):
        
        # Stores the co-ords of the finger tips
        fingertip_list = []

        try:
            fingertip_list.append(end_pts[1])
            fingertip_list.append(self.midPoint(end_pts[0], start_pts[1]))
            fingertip_list.append(self.midPoint(end_pts[3], start_pts[0]))
            fingertip_list.append(self.midPoint(end_pts[2], start_pts[3]))
            fingertip_list.append(start_pts[2])
        except:
            "error"

        return fingertip_list


    """
    Computes the rotation angle of the image 
        Parameters  : img <numpy array>
        Returns     : rotated <numpy array>                                         
    """
    def computeRotation(self, image):

        # Finds midpoint of middle finger convave point
        contours_midpoint  = self.midPoint(self.property_concaves[1], self.property_concaves[2])
        # Finds co-ords of middle finger fingertip
        middle_finger_X    = self.property_fingers[2][0]
        middle_finger_Y    = self.property_fingers[2][1]

        # Finds height and width of image
        (h, w)             = image.shape[:2]
        # Anchors the image at the concave of the middle finger for rotation
        (cX, cY)           = (int(contours_midpoint[0]), int(contours_midpoint[1]))

        opp                = abs(middle_finger_X - contours_midpoint[0])
        middleFinger       = [middle_finger_X, middle_finger_Y]
        adj                = math.dist(middleFinger, contours_midpoint)
        rotationAngle      = math.degrees(math.atan(opp / adj))

        # Determines the direction to rotate the image
        if middle_finger_X < contours_midpoint[0]:
            rotationAngle  = 360 - rotationAngle

        # Performs the actual roation of image
        M        = cv.getRotationMatrix2D((cX, cY), rotationAngle, 1.0)
        rotated  = cv.warpAffine(image, M, (w, h))

        return rotated


    """
    Scales the output images (processed + original images) to fit the display window
        Parameters  : image  <numpy array>
        Returns     : <numpy array>
    """
    def resizeImage(self, image, width, height, scale):
        
        width          = int(width * scale / 100)
        height         = int(height * scale / 100)
        dim            = (width, height)
        resized_image  = cv.resize(image, dim, interpolation=cv.INTER_AREA)
        
        return np.array(resized_image)


    """
    Converts the numpy array image to an image which can be displayed on tkinter 
        Parameters  : 
        Returns     : img <ImageTk.PhotoImage>                                        
    """
    def displayProcessedImage(self, original_bool, ideal_bool):

        if original_bool and not ideal_bool:
            resized = self.resizeImage(
                self.overlayed_images_basic,
                self.overlayed_images_basic.shape[1],
                self.overlayed_images_basic.shape[0],
                25,
            )
        
        elif ideal_bool and not original_bool:
            resized = self.resizeImage(
                self.overlayed_images_ideal,
                self.overlayed_images_ideal.shape[1],
                self.overlayed_images_ideal.shape[0],
                25,
            )
        
        elif ideal_bool and original_bool:
            resized = self.resizeImage(
                self.overlayed_images_all,
                self.overlayed_images_all.shape[1],
                self.overlayed_images_all.shape[0],
                25,
            )
        else:
            resized = self.resizeImage(
                self.image_rotated,
                self.image_rotated.shape[1],
                self.image_rotated.shape[0],
                25,
            )

        return ImageTk.PhotoImage(image=Image.fromarray(resized))
       
    """
    Composes an image by combining two images 
        Parameters  : original_image <numpy array>, final_image <numpy array>
        Returns     : <numpy array>                                       
    """
    def overlayImages(self, original_image, final_image):
        
        # Gets size for output image
        width   = max(original_image.shape[1], final_image.shape[1])
        height  = max(original_image.shape[0], final_image.shape[0])

        o_i     = self.resizeImage(original_image, width, height, 100)
        f_i     = self.resizeImage(final_image, width, height, 100)

        dst     = cv.addWeighted(o_i, 0.7, f_i, 0.3, 0)
        
        return np.array(dst)
