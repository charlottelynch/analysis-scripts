#!/usr/bin/env python3

##############################################################
# Script to average a set of json files for radius,          #
# hydrophobicity, water density and (zeroed) free energy     #
# and then plot the averaged values over the original values.#
# Also saves the averaged values to file.                    #
##############################################################
# Notes to run:                                              #
# -supply path to files and then run! :)                     #
##############################################################


import json                             # read in JSON files
from matplotlib import pyplot as pl     # plotting facilities
import argparse                         # parse command line arguments
#import glob
from cycler import cycler


# get parameters from user input:
parser = argparse.ArgumentParser()
parser.add_argument(
    "-filename",
    nargs = "?",
    const = "*.json",
    default = "*.json")
parser.add_argument("-dpi",
    nargs = "?",
    const = 300,
    default = 300,
    type = int)
args = parser.parse_args()


json_files = ["/path1/file1.json", 
              "/path2/file2.json",
              "/path3/file3.json",
              "/path4/file4.json",
              "/path5/file5.json",
              "/path6/file6.json"]


def load_data(file_name,y_axis_name,x_min,x_max):
    """
    file_name is the path to the file; y_axis_name is the key in the pathwayProfile dictionary
    Returns list of tuples of (x,y)
    """
    with open(file_name, "r") as file_handle:
        data_set = json.load(file_handle)
    x_series = data_set["pathwayProfile"]["s"]
    y_series = data_set["pathwayProfile"][y_axis_name]
    return [(x,y) for x,y in zip(x_series,y_series) if x >= x_min and x <= x_max]

# Test:
#load_data(json_files[0],"radiusMean",-5.5,2.5)[:5]
# Result:
#[(-5.391003608703613, 1.0),
# (-5.3820929527282715, 1.0000007152557373),
# (-5.37318229675293, 1.000001072883606),
# (-5.364271640777588, 1.000001072883606),
# (-5.355360984802246, 1.0000017881393433)]


def get_bin(x,bin_width):
    """
    Within a given bin width, this determines how the data would be modified to the centroid of the bin
    """
    return bin_width*round(x/bin_width)

# Test1:
#get_bin(5.123,0.2)
# Result: 5.2

# Test2:
#get_bin(5.101,0.2)
# Result: 5.2

#Test 3:
#get_bin(5.100,0.2)
# Result: 5.0

# Test 4:
#type(get_bin(1,0.01))
# Result: float


def add_bins_to_data(xy_series,bin_width):
    """
    Makes tuple with three floats for x, the x centroid within the bin, and y from a tuple with just 
    x and y floats. N.B. uses function bin_width as an argument!
    """
    return[(x,get_bin(x,bin_width),y) for x,y in xy_series]

# Test:
#add_bins_to_data(
#    [(1.34,4.5),(1.36,4.50001)],
#    0.11
#)
# Result: [(1.34, 1.32, 4.5), (1.36, 1.32, 4.50001)]


def average_by_bin(xbin_y_series):
    """
    Averages the y values for each x bin centroid value.
    It does this by creating a key (via creating a dictionary) for each x bin centroid value and 
    then averages the y values for the data with the same x centroid value. It then sorts the 
    keys in ascending order of bin value. 
    Returns list of tuples containing bin value and average y.
    """
    bin_values = {} #{} creates empty dictionary
    # Key of dictionary is the x bin centroid, and the value is a list of y values.
    for x,x_bin,y in xbin_y_series:
        if x_bin not in bin_values:
            bin_values[x_bin] = []
        bin_values[x_bin].append(y)
    # Below takes averages of the y values from a list of bin values which has been formed 
    # from the dictionary (.items does the latter)
    unsorted_averages = [(key,sum(value)/len(value)) for key,value in bin_values.items()] 
    # Below sorts the lists in order of bin value. 
    return sorted(unsorted_averages)

# Test1:
#average_by_bin([(4.35,4.4,6),(4.37,4.4,6.5)])
# Result: [(4.4, 6.25)]

#Test2:
#average_by_bin([(4.37,4.4,6.5),(4.35,4.4,6)])
# Result: [(4.4, 6.25)]
        

def load_bin_and_average(file_name,yaxis_name,bin_width,x_min,x_max):
    """
    Loads the data set from the file, creates the bins and averages the y values 
    with the same bin value - i.e. sticks the above functions together
    """
    data_set = load_data(file_name,yaxis_name,x_min,x_max)
    binned_data_set = add_bins_to_data(data_set,bin_width)
    averaged_binned_data_set = average_by_bin(binned_data_set)
    return averaged_binned_data_set

# Test:
#averaged_data = load_bin_and_average(json_files[0],"radiusMean",0.02,-5.0,2.0)
#pl.scatter([x for x,y in averaged_data], [y for x,y in averaged_data])


def offset_value(file_name,yaxis_name,bin_width,x_min,x_max):
    """
    CIL 07/01/21 - Extracts the last y value of the binned data set
    N.B. Therefore be careful to make sure that the last bin is outside the pore! 
    TO DO: Could hard code the offset value if needed at a later stage?
    """
    data_set = load_bin_and_average(file_name,yaxis_name,bin_width,x_min,x_max)
    #extract last y data point
    offset = data_set[-1]
    return offset

# Test:
#datum = offset_value(json_files[1],"energyMean",0.01,-5.0,3.5)
#print(datum)
# Result: (3.5, -0.008207559585571289)


def translate_data(file_name,yaxis_name,bin_width,x_min,x_max):
    """
    CIL 07/01/21 Translates binned data by offset_value
    """
    data_set = load_bin_and_average(file_name,yaxis_name,bin_width,x_min,x_max)
    offset_point = offset_value(file_name,yaxis_name,bin_width,x_min,x_max)
    print(offset_point[1])
    offset_data_set = [(x, y - offset_point[1]) for x, y in data_set]
    return offset_data_set

# Test:
#translated_data = translate_data(json_files[1],"energyMean",0.01,-5.0,3.5)
#pl.scatter([x for x,y in translated_data], [y for x,y in translated_data])


def list_yaxes(file_name):
    """
    Opens a file and gives you all the keys in the pathway profile dictionary 
    i.e. just lets you know what variables are called so you can access them
    """
    with open(file_name) as file_handle:
        data = json.load(file_handle)
    return data["pathwayProfile"].keys()


def load_all_bin_and_average(file_names,yaxis_name,bin_width,x_min,x_max):
    """
    Loads all data files, and averages the y values for a given 
    bin value
    N.B. 08/01/21 Use this for non-translated data! 
    """
    all_data = []
    for file_name in file_names:
        print(file_name,list_yaxes(file_name))
        # Averages the y values for a given bin value within a file
        all_data += load_bin_and_average(file_name,yaxis_name,bin_width,x_min,x_max)
    # Averages the (already averaged) y values between the files
    # average_by_bin expects an x value (i.e. 3-valued tuples) and None provides it with 
    # that extra value with a value of none - it would break if the placeholder wasn't there
    return average_by_bin([(None,x_bin,y) for x_bin,y in all_data])

# Test:
#pl.figure(figsize=[10,10])
#averaged_data = load_all_bin_and_average(json_files,"radiusMean",0.01,-5.0,2.0)
#pl.scatter([x for x,y in averaged_data], [y for x,y in averaged_data],label="combined")
#averaged_data = load_bin_and_average(json_files[0],"radiusMean",0.01,-5.0,2.0)
#pl.scatter([x for x,y in averaged_data], [y for x,y in averaged_data])
#averaged_data = load_bin_and_average(json_files[1],"radiusMean",0.01,-5.0,2.0)
#pl.scatter([x for x,y in averaged_data], [y for x,y in averaged_data])
#pl.legend()


def load_all_translated_bin_and_average(file_names,yaxis_name,bin_width,x_min,x_max):
    """
    CIL 08/01/21 Loads all data files which are binned and translated, and averages the y values for a given 
    bin value
    """
    all_data = []
    for file_name in file_names:
        print(file_name,list_yaxes(file_name))
        # Averages the y values for a given bin value within a file
        all_data += translate_data(file_name,yaxis_name,bin_width,x_min,x_max)
    # Averages the (already averaged) y values between the files
    # average_by_bin expects an x value (i.e. 3-valued tuples) and None provides it with 
    # that extra value with a value of none - it would break if the placeholder wasn't there
    return average_by_bin([(None,x_bin,y) for x_bin,y in all_data])

# Test:
#pl.figure(figsize=[10,10])
#averaged_data = load_all_translated_bin_and_average(json_files,"energyMean",0.01,-5.0,3.5)
#pl.scatter([x for x,y in averaged_data], [y for x,y in averaged_data],label="combined")
#averaged_data = translate_data(json_files[0],"energyMean",0.01,-5.0,3.5)
#pl.scatter([x for x,y in averaged_data], [y for x,y in averaged_data])
#averaged_data = translate_data(json_files[1],"energyMean",0.01,-5.0,3.5)
#pl.scatter([x for x,y in averaged_data], [y for x,y in averaged_data])
#pl.legend()


##########################################################
# Plots mean radius profile, averaged over all data sets #
##########################################################
# N.B. I have found that bin_width=0.01 for averaging data leads to noise, bin_width=0.02 is fine.

pl.figure("radius_profile")
pl.rc('axes', prop_cycle=(cycler('color', ['m', 'r', 'b', 'limegreen', 'darkorange', 'c', 'k', 'olive', 'yellowgreen'])))

averaged_data = load_bin_and_average(json_files[0],"radiusMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[1],"radiusMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[2],"radiusMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[3],"radiusMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[4],"radiusMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[5],"radiusMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_all_bin_and_average(json_files,"radiusMean",0.02,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data],label="Average", linewidth=1.5)

pl.tick_params(labelsize=14)

#pl.margins(x = 0)
#pl.title("Radius", fontsize=20)
pl.xlabel("s (nm)", fontsize=16)
pl.ylabel("R (nm)", fontsize=16)
pl.tight_layout() #ensures the axis labels don't get cut off

pl.legend(fontsize=16)
pl.savefig("time_averaged_radius_profile-averaged.png", dpi = args.dpi)

pl.close("radius_profile")

##################
# Plotting Notes #
##################
# pl.xlim((-5,3.5)) sets limits of x axis
# pl.ylim((-1,20)) sets limits of y axis


##################################################################
# Plots mean hydrophobicity profile, averaged over all data sets #
##################################################################

pl.figure("hydrophobicity_profile")
pl.rc('axes', prop_cycle=(cycler('color', ['m', 'r', 'b', 'limegreen', 'darkorange', 'c', 'k', 'olive', 'yellowgreen'])))

averaged_data = load_bin_and_average(json_files[0],"pfHydrophobicityMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[1],"pfHydrophobicityMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[2],"pfHydrophobicityMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[3],"pfHydrophobicityMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[4],"pfHydrophobicityMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[5],"pfHydrophobicityMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_all_bin_and_average(json_files,"pfHydrophobicityMean",0.02,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data],label="Average", linewidth=1.5)

pl.tick_params(labelsize=14)

#pl.margins(x = 0)

pl.xlabel("s (nm)", fontsize=16)
pl.ylabel("Hydrophobicity (a.u.)", fontsize=16)
pl.tight_layout() #ensures the axis labels don't get cut off

pl.legend(fontsize=16)
pl.savefig("time_averaged_hydrophobicity_profile-averaged.png", dpi = args.dpi)

pl.close("hydrophobicity_profile")


##################################################################
# Plots mean water density profile, averaged over all data sets #
##################################################################

pl.figure("density_profile")
pl.rc('axes', prop_cycle=(cycler('color', ['m', 'r', 'b', 'limegreen', 'darkorange', 'c', 'k', 'olive', 'yellowgreen'])))

averaged_data = load_bin_and_average(json_files[0],"densityMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[1],"densityMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[2],"densityMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[3],"densityMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[4],"densityMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[5],"densityMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_all_bin_and_average(json_files,"densityMean",0.02,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data],label="Average", linewidth=1.5)

pl.tick_params(labelsize=14)

#pl.margins(x = 0)

pl.xlabel("s (nm)", fontsize=16)
pl.ylabel("Water density (nm$^{-3}$)", fontsize=16)
pl.tight_layout() #ensures the axis labels don't get cut off

pl.legend(fontsize=16)
pl.savefig("time_averaged_water-density_profile-averaged.png", dpi = args.dpi)

pl.close("density_profile")


##################################################################
# Plots mean free energy profile, averaged over all data sets    #
# SHOULDN'T USE AS ENERGIES NOT TRANSLATED, but good to check!   #
##################################################################

pl.figure("energy_profile")
pl.rc('axes', prop_cycle=(cycler('color', ['m', 'r', 'b', 'limegreen', 'darkorange', 'c', 'k', 'olive', 'yellowgreen'])))

averaged_data = load_bin_and_average(json_files[0],"energyMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[1],"energyMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[2],"energyMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[3],"energyMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[4],"energyMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_bin_and_average(json_files[5],"energyMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_all_bin_and_average(json_files,"energyMean",0.02,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data],label="Average", linewidth=1.5)

pl.tick_params(labelsize=14)

#pl.margins(x = 0)

pl.xlabel("s (nm)", fontsize=16)
pl.ylabel("Free Energy ($\mathrm{k_{B}T}$)", fontsize=16)
pl.tight_layout() #ensures the axis labels don't get cut off

pl.legend(fontsize=16)
pl.savefig("time_averaged_free-energy_profile-averaged.png", dpi = args.dpi)

pl.close("energy_profile")


##################################################################
# Plots mean free energy profile,                                #
# having zeroed the energies by the outside pore energy,         #
# averaged over all data sets.                                   #
# Also prints out the amount by which the data is translated.    #
##################################################################

pl.figure("energy_profile")
pl.rc('axes', prop_cycle=(cycler('color', ['m', 'r', 'b', 'limegreen', 'darkorange', 'c', 'k', 'olive', 'yellowgreen'])))

averaged_data = translate_data(json_files[0],"energyMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = translate_data(json_files[1],"energyMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = translate_data(json_files[2],"energyMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = translate_data(json_files[3],"energyMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = translate_data(json_files[4],"energyMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = translate_data(json_files[5],"energyMean",0.01,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data], linewidth=1)
averaged_data = load_all_translated_bin_and_average(json_files,"energyMean",0.02,-5.0,3.5)
pl.plot([x for x,y in averaged_data], [y for x,y in averaged_data],label="Average", linewidth=1.5)

pl.tick_params(labelsize=14)

#pl.margins(x = 0)

pl.xlabel("s (nm)", fontsize=16)
pl.ylabel("Free Energy ($\mathrm{k_{B}T}$)", fontsize=16)
pl.tight_layout() #ensures the axis labels don't get cut off

pl.legend(fontsize=16)
pl.savefig("time_averaged_free-energy_profile-averaged-translated.png", dpi = args.dpi)

pl.close("energy_profile")

########################
# Saving data to files #
########################

### Saves averaged radius data to a new file ###
# N.B. Use bin_width=0.02 not 0.01 to reduce noise! #
averaged_data = load_all_bin_and_average(json_files,"radiusMean",0.02,-5.0,3.5)

with open("averaged_radius.dat", "w") as file_handle:
    json.dump(list(averaged_data), file_handle)


### Saves averaged hydrophobicity data to a new file ###
# N.B. Use bin_width=0.02 not 0.01 to reduce noise! #
averaged_data = load_all_bin_and_average(json_files,"pfHydrophobicityMean",0.02,-5.0,3.5)

with open("averaged_hydrophobicity.dat", "w") as file_handle:
    json.dump(list(averaged_data), file_handle)


### Saves averaged water density data to a new file ###
# N.B. Use bin_width=0.02 not 0.01 to reduce noise! #
averaged_data = load_all_bin_and_average(json_files,"densityMean",0.02,-5.0,3.5)

with open("averaged_water_density.dat", "w") as file_handle:
    json.dump(list(averaged_data), file_handle)


###Saves translated and averaged energy to new file###
# N.B. Use bin_width=0.02 not 0.01 to reduce noise! #
averaged_data = load_all_translated_bin_and_average(json_files,"energyMean",0.02,-5.0,3.5)

with open("averaged_and_translated_energy.dat", "w") as file_handle:
    json.dump(list(averaged_data), file_handle)

