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
    
    ##Conectividad 8
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            #If the pixel is not background
            regionA = None
            regionB = None
            regionC = None
            regionD = None
            if padded_image[i][j] == 255:
                ##Check left pixel
                if (padded_image[i][j-1]) == 255:
                    regionA = find_pixel_group(regions, (j-1,i))
                ##Check up pixel
                if (padded_image[i-1][j]) == 255:
                    regionB = find_pixel_group(regions, (j,i-1))
                ##Check up-left
                if (padded_image[i-1][j-1]) == 255:
                    regionC = find_pixel_group(regions, (j-1,i))
                ##Check up-right
                if (padded_image[i-1][j+1]) == 255:
                    regionD = find_pixel_group(regions, (j-1,i))

                regionF = None
                reference = False
                origin = []

                # Check all regions, update for smallest found region
                if regionA:
                    regionF = regionA

                if regionB:
                    if regionF is not None:
                        reference = True
                        if int(regionB) < int(regionF):
                            origin.append(regionF)
                            regionF = regionB
                        else:
                            origin.append(regionB)
                    else:
                        regionF = regionB

                if regionC:
                    if regionF is not None:
                        reference = True
                        if int(regionC) < int(regionF):
                            origin.append(regionF)
                            regionF = regionC
                        else:
                            origin.append(regionC)
                    else:
                        regionF = regionC

                if regionD:
                    if regionF is not None:
                        reference = True
                        if int(regionD) < int(regionF):
                            origin.append(regionF)
                            regionF = regionD
                        else:
                            origin.append(regionD)
                    else:
                        regionF = regionD

                # Update references for all regions in origin to point to the smallest region (regionF)
                if reference:
                    destiny = regionF  # Set the destiny to the smallest region
                    for orig in origin:
                        # Ensure we don't set a region's reference to itself
                        if orig != destiny:
                            if regions[orig]["reference"] is None:
                                regions[orig]["reference"] = destiny
                            else:
                                if int(regions[orig]["reference"]) > int(destiny):
                                    regions[regions[orig]["reference"]]["reference"] = destiny
                                    regions[orig]["reference"] = destiny


                #If no region was found, create new entry to dictionary and add current element
                if regionF == None:
                    regions[str(regionN)] = {"members": {(j,i)}, "reference": None}
                    regionN += 1
                else:
                    # A region was found, add pixel to region members
                    regions[regionF]["members"].add((j, i))


    
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
                    if regions[current]["reference"] != current:
                        target = regions[current]["reference"]
                        for pixel in regions[current]["members"]:
                            regions[target]["members"].add(pixel)
                    else:
                        break
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
