'''
Main Driver for XHAND image processing
Contributed to by:
    Lucas Carr      |   CRRLUC003
    Gadi Friedman   |   FRDGAD001
    Gabriel Marcus  |   MRCGAB004

2022-08-08
University of Cape Town
Capstone Project: X-Hand Image Processing
'''


from    ast import Div
from    gettext import find
import  os
from    queue import Empty
from    re import T
import  shutil
import  cv2 as cv
import  numpy as np
from    PIL import Image
from    ImageObject import ImageObject
from    ImageHolder import ImageHolder
import  imageio
from    operator import itemgetter
import  statistics
import  UserInterface


"""
- Acts primarily as a driver class for the overall program
- Has some additional features for post-hoc functionality
"""
input_path        = "No input path specified"
output_path       = "Images/Output Images/"
image_containter  = ImageHolder()


"""
Auxilliry function for readInFiles
        Parameters  : path <String>, filename <String>
        Returns     : void
"""
def helper(path, filename): 

    if (filename.endswith(".png")):
        raw_image   = cv.imread(os.path.join(path, filename),0)
        source_img  = np.array(raw_image)
        image_containter.addImage(ImageObject(source_img, filename))


"""
Reads in images into the program
        Parameters  : path <String>
        Returns     : void
"""
def readInFiles(path):

    for filename in os.listdir(path):
        helper(path, filename)

    return


"""
Writes all images in the given ImageHolder to the specified output path
        Parameters  : output_path <String>, image_container <ImageHolder>
        Returns     : void
"""
def writeImages(output_path, image_containter):

    images = image_containter.getImageObjects()
    
    for img in images:
        imageio.imwrite((output_path + img.filename), img.image_rotated)

    
    return


"""
- Allows the user to give a target (base) image, and data of interest (ie. Middle Finger Length, Bone 
  Density)
- Computes a similarity matrix of all hands, based on some the target attribute
- The similarity matrix is determined by finding the distances between attribute value in all hand pairs
- Mean of similarity of matrix is then taken, and used as a baseline for what constitutes "similarity" 
  (if hand_pair.similarity < mean_similarity, hand_pair is considered to be similar)
- Returns all hand pairs that are similar 

        Parameters  : compare_to <ImageObject>, data <List>
        Returns     : void
"""
def findSimilarHands(compare_to,data):



    # Determines the amount of data to be used in construction of matrices
    n                 = len(data)
    object_list       = []
    # Creates empty matrices to store distances and similarities
    dist_matrix       = np.zeros((n,n))  
    full_object_list  = np.empty((n,n), dtype=object)

    # Computes matrice values
    for i in range(n):
        for j in range(n): 
            dist_matrix[i,j]       = abs(data[i][1]-data[j][1])
            full_object_tuple      = ([data[i][0],data[j][0],dist_matrix[i,j]])
            full_object_list[i,j]  = full_object_tuple
        
        object_list.append(data[i][0])

    sum_of_cells      = 0
    comparisons_made  = 0


    # Finds total sum of matrix 
    for i in range(n):
        for j in range(n):
            sum_of_cells      += dist_matrix[i,j]
            comparisons_made  += 1
    
    # Finds mean distance (to be used for determining if pairs are similar)
    avg_dist      = sum_of_cells/(comparisons_made-n)
    
    # Iterates through all Hand Pairs and adds similar hands to similarHands <List>
    similarHands  = []   
    for i in range(0,n-1):
        for j in range(i+1,n):
            if dist_matrix[i,j] < avg_dist:
                if full_object_list[i,j][0] == compare_to:

                    correct_hand = full_object_list[i,j][1]
                    similarHands.append(correct_hand)

                elif full_object_list[i,j][1] == compare_to:

                    correct_hand = full_object_list[i,j][0]
                    similarHands.append(correct_hand)
   
   # Writes all similar hands to a file
    temp_location  = (output_path + "Similar Hands/")
    if os.path.exists(temp_location):
        shutil.rmtree(temp_location)
    os.makedirs(temp_location)

    cv.imwrite(temp_location+compare_to.filename,compare_to.image_rotated)

    for hand in similarHands:
        
        cv.imwrite(temp_location+hand.filename,hand.image_rotated)

    return


"""
- Allows the user to specify a hand attribute of interest, and the amount of standard deviations away 
  (from the center of the distribution of all hands, based on the given attribute) they want hands to 
  be returned of
- Attribute searched against can be bone density or finger length (of index, middle and ring fingers)
- Writes the similar hands to a file
        Parameters  : attribute <int>, deviations <int>
        Returns     : <Tuple(<List>,<List>)>
"""
# for attribute == -1 : Searches against bone density
# for attribute == 1  : Searches against index finger length
# for attribute == 2  : Searches against middle finger length
# for attribute == 3  : Searches against ring finger length
def findCenterOfDist(attribute,deviations):
    
    # Label for graph
    graph_label = ''

    # Gets all images to be checked 
    images         = image_containter.getImageObjects()
    full_data_set  = []

    # Stores the bone density of all images
    if attribute == -1:
        for image_object in images:
            temp_tuple = (image_object.bone_percentage, image_object)
            full_data_set.append(temp_tuple)
            graph_label = "Bone Density"

    # Stores the values of the relevant finger length
    if attribute  > -1:
        graph_label = "Finger Length"
        for image_object in images:
            temp_tuple = (image_object.finger_lengths[attribute],image_object)
            full_data_set.append(temp_tuple)

    full_data_set.sort(key=itemgetter(0))
    quantity      = []
    mean_of_data  = 0

    # Calculates sum of the data
    for item in full_data_set:
        quantity.append(item[0])
        mean_of_data = mean_of_data + item[0]
    
    # Calculates mean of the data
    mean_of_data      = mean_of_data/len(full_data_set)
    
    # Calculates the standard deviation of the data
    if len(full_data_set)>1:
        standard_dev = statistics.stdev(quantity)
    else:
        standard_dev  = 0

    close_hands      = []
    not_close_hands  = []

    # Sets the bounds for valid data
    upper_bound  = mean_of_data + deviations*standard_dev
    lower_bound  = mean_of_data - deviations*standard_dev

    # Finds the hands that have specified attribute within the calculated bounds
    for item in full_data_set:
        if lower_bound <= item[0]:
            if item[0] <= upper_bound:
                close_hands.append(item[1])
            else:
                not_close_hands.append(item[1])
        else:
            not_close_hands.append(item[1])    

    # Stores the stuff
    temp_location  = (output_path + "Hands_inside_" + str(deviations)+'_stdevs_of_mean/')
    if os.path.exists(temp_location):
        shutil.rmtree(temp_location)
    os.makedirs(temp_location)

    for hand in close_hands:
 
        cv.imwrite(temp_location+hand.filename,hand.image_rotated)

    return (close_hands,not_close_hands)


"""
- Allocates images into clusters based on their hand's bone density
- Allows for the amount of clusters to be determined by the user (k)
- Creates files for each cluster and stores clustered images into them
        Parameters  : amount_clusters <int>
        Returns     : void
"""
def computeGroupsBD(amount_clusters):
    
    # Gets all images to be checked 
    images         = image_containter.getImageObjects()
    

    # Creates and populates a list with all of the images and their bone densities (as tuples)
    full_data_set  = []
    for image_object in images:
        temp_tuple  = (image_object.bone_percentage, image_object)
        full_data_set.append(temp_tuple)
    
    # Order the images by bone density
    full_data_set.sort(key=itemgetter(0))

    # Error prevention in the event that user wants more clusters than there are objects in the data set
    if len(full_data_set) < amount_clusters:
        amount_clusters  = len(full_data_set)

    final_clusters           = []

    # Finds amount of data points to be in the initial clusters
    amount_in_initial_groups  = len(full_data_set)//amount_clusters
    
    # Triggers if the total length of data cannot fill the total clusters
    if amount_in_initial_groups == 0:
        amount_in_initial_groups = 1

    # Finds the amount of clusters that have an additional data point at the beginning
    extras  = len(full_data_set)%amount_clusters
    
    # Creates the initial clusters
    finalPointer  = 0
    for i in range(amount_clusters):
       
        tempList = []

        if extras > 0:
            xtra = 1
        else:
            xtra = 0

        for j in range(amount_in_initial_groups+xtra):   
            finalPointer  = i*amount_in_initial_groups+j
            tempList.append(full_data_set[finalPointer])
        
        final_clusters.append(tempList)

        if extras > 0:
            extras -= 1
        
    # Calculate centers of the initial clusters
    averages  = []
    for i in range(amount_clusters):
        total_of_cluster = 0
        for j in range(len(final_clusters[i])):
            total_of_cluster = total_of_cluster + final_clusters[i][j][0]

        averages.append(total_of_cluster/len(final_clusters[i]))

    # Performs  actual clustering  
    changeHasOccured = True
    while changeHasOccured:    
        
        emptyClusterVal = 0
        emptyClusterFound = False
        averages = []

        for i in range(amount_clusters):
            total_of_cluster = 0
            for j in range(len(final_clusters[i])):
                total_of_cluster = total_of_cluster + final_clusters[i][j][0]
            if len(final_clusters[i])!=0:
                averages.append(total_of_cluster/len(final_clusters[i]))
            else: 
                amount_clusters    -=1
                emptyClusterFound  = True
                emptyClusterVal    = i

        # Empty clusters may occur if bad K chosen, prevents errors when this happens
        if emptyClusterFound:
            final_clusters.pop(emptyClusterVal)

        # ChangeHasOccured monitors if items have moved, to see if clustering needs to stop or not
        changeHasOccured = False
        for i in range(amount_clusters):

            deduct_from_j  = 0

            closestCluster = i
            for j in range(len(final_clusters[i])):
                
                diffsFromCenter  = []

                # Distance between point and center of it's cluster            
                shortestDist  = abs(averages[i] - final_clusters[i][j+deduct_from_j][0])
                # Distance between point and center of other clusters
                for k in range(0,amount_clusters):
                    tempDist  = (abs(averages[k] - final_clusters[i][j+deduct_from_j][0]))

                    # Ff distance between point and cluster is shorter than current shortest distance, 
                    # set closest cluster to k and set new shortest dist
                    if tempDist < shortestDist:

                        closestCluster  = k
                        shortestDist    = tempDist
                
                # Moves items to different cluster 
                if averages[i] != averages[closestCluster]:
                    changeHasOccured  = True
                    temp              = final_clusters[i][j+deduct_from_j]
                    final_clusters[i].pop(j+deduct_from_j)
                    deduct_from_j     -= 1
                    final_clusters[closestCluster].append(temp)

    # Stores clusters of images in folders
    for num, cluster in enumerate(final_clusters):
        temp_location  = (output_path + "Cluster_" + str (num)+'/')

        if os.path.exists(temp_location):
            shutil.rmtree(temp_location)
            
        os.makedirs(temp_location)

        for enum, item in enumerate(cluster):
            cv.imwrite(temp_location+str(enum)+item[1].filename, item[1].image_rotated)

    return


"""
Main method
        Parameters  : 
        Returns     : void
"""
def main():
    UserInterface.main()


"""
Calls main method
        Parameters  : 
        Returns     :  void 
"""
if __name__ == "__main__":
    main()

