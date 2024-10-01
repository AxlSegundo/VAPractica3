import numpy as np
import random
import cv2
from get_plate import main as get_plate
from compact import main as binarize
import os

def find_pixel_group(groups, pixel):
    for group_name, data in groups.items():
        if pixel in data['members']:
            return group_name  # Return the name of the group
    return None  # Return None if the pixel is not found in any group


def main(imgnumber, imgpath = "img\\cropped_parking_lot_107.JPG"):
    plate = get_plate(imgpath)
    image = binarize(plate)
    image = (255-image)
    
    
    padded_image = np.pad(image, 1)
    regions = {}
    regionN = 0
    cv2.imwrite("Out.jpg", padded_image)
    
    #Conectividad 4
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            #If the pixel is not background
            regionA = None
            regionB = None
            if padded_image[i][j] == 255:
                ##Check left pixel
                if (padded_image[i][j-1]) == 255:
                    regionA = find_pixel_group(regions, (j-1,i))
                ##Check up pixel
                if (padded_image[i-1][j]) == 255:
                    regionB = find_pixel_group(regions, (j,i-1))

                regionF = None
                reference = False
                
                #If two regions were found
                if regionA and regionB:
                    #If they are the same
                    if regionA == regionB:
                        regionF = regionA
                    #If they're different
                    elif int(regionB)<int(regionA):
                        regionF = regionB
                        origin = regionA
                        destiny = regionB
                        reference = True
                    else:
                        regionF = regionA
                        origin = regionB
                        destiny = regionA
                        reference = True
                else:
                    #Check if any region was found
                    if regionA:
                        regionF = regionA
                    else:
                        regionF = regionB

                #If no region was found, create new entry to dictionary and add current element
                if regionF == None:
                    #print(i, ",", j)
                    regions[str(regionN)] = {"members": {(j,i)}, "reference": None}
                    regionN += 1
                else:
                    #A region was found, add pixel to region members
                    regions[regionF]["members"].add((j,i))
                    #If a reference was found
                    if reference:
                        # Check if there is no existing reference
                        if regions[origin]["reference"] is None:
                            regions[origin]["reference"] = destiny  # Assign destiny as the reference
                        else:
                            # Compare to set to earlier group
                            if int(regions[origin]["reference"]) > int(destiny):
                                regions[regions[origin]["reference"]]["reference"] = destiny
                                regions[origin]["reference"] = destiny 


    
    #After all pixels have been classified
    death_row = []


    for region in regions:  # Check all registered regions
        if regions[region]["reference"] is not None:  # If a region has a reference
            # Add all its pixels to the reference
            target = regions[region]["reference"]
            for pixel in regions[region]["members"]:
                regions[target]["members"].add(pixel)  # Ensure members is a set
            death_row.append(region)  # Mark the region for deletion
            #Follow the line up until no reference is present
            while True:
                ##This could be included with the section above
                current = target
                if regions[current]["reference"] is not None:
                    target = regions[current]["reference"]
                    for pixel in regions[current]["members"]:
                        regions[target]["members"].add(pixel)
                else:
                    break



    # Throw the useless ones to the pigs
    for key in death_row:
        del regions[key]


    #Now paint the streets with their entrails
    colors = {}
    for region in regions:
        colors[region] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
    marked_image = np.copy(plate)
    for region, details in regions.items():
        color = colors[region]
        for pixel in details["members"]:
            x, y = pixel
            # Mark the pixel with the assigned color
            marked_image[y, x] = color
            
    #Finally, pose their corpse on a pike in the city square for all to see
    #cv2.imshow("image", marked_image)
    #cv2.waitKey(0)
    out_path = "output/image" + str(imgnumber) + ".jpg"
    cv2.imwrite(out_path,marked_image) 



directory = os.fsencode("D:\\Code\\Work\\Sem5\\Segmentacion\\img")
count = 0
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".JPG"):
        main(count,os.path.join(directory, filename))
        count += 1