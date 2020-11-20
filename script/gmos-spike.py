# Import Python Packages.
import numpy as np
from pyraf import iraf
from pyraf.iraf import gemini, gemtools, gmos, onedspec
import os
from astropy.io import fits
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

# Directory path for the uncalibrated files.
raw_path = '/raw/'

# Print the central wavelength and class for all files in the directory.
# The Sciece Object file must match its wavelength coverage with BIAS,
# FLAT and ARC calibration files.
print('')
print("The available values for central wavelength in this directory are: ")
print('')
print('ObsClass \ CentWave')
print('')
iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path), #IRAF task 'hselect'.
            'obsclass && GrWlen', 'ObsType="OBJECT"')
print('')

# Empty lists for saving the names of the selected files.
obj_std_name=[]
obj_sci_name=[]
arc_std_name=[]
arc_sci_name=[]

bias_std_list=[]
flat_std_list=[]
bias_obj_list=[]
flat_obj_list=[]

def selec_std():
    """ Select a Standard Star and its calibration files matching their
    central wavelength and CCD binning. """

    while True:
        try:
            # Ask for a central wavelength value.
            wavelength = int(input("Type the central wavelength for the "
                                   "STANDARD STAR: "))
            # Parameters for the IRAF task 'hselect'.
            select_std = ('ObsType="OBJECT" && obsclass?= "partnerCal" && '
                         'CentWave = {}'.format(wavelength))

            print('')
            # Print the selected parameters.
            print("Selecting " + select_std)

            # Confirm the existence of files with the selected parameters.
            selected_files=[]
            selected_files.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                                    '$I', select_std, Stdout=1))

            if selected_files == [[]]:
                print('')
                print("There is no file matching the specified value.")

            else:
                print('')
                # Print the number of STANDARD STAR files matching the specified
                # values.
                print("It has been found {} STANDARD STAR file(s) matching the "
                                "specified values:".format(len(selected_files[0])))
                print('')
                print(" Name \ CCDsum ")
                print('')

                std_title=[]
                std_name=[]
                std_ccdsum=[]
                std_name.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                                '$I', select_std, Stdout=1)) # File name.
                std_ccdsum.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                                 '$Ccdsum', select_std, Stdout=1)) # File CCD Binning.
                std_title.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                                '$title', select_std, Stdout=1)) # File title
                for j in range(len(std_name[0])):
                    # Print STANDARD STAR names, CCD binning and title.
                    # Remove '[2,inherit=yes]' and 'raw_path' from their names.
                    print(std_name[0][j].replace('[2,inherit=yes]','').replace(raw_path,''),
                            std_ccdsum[0][j], std_title[0][j])

                break

        except (NameError, SyntaxError,IndexError):
            print('')
            print("Check if you typed a correct central wavelength. ")

    # Select a file matching the values for central wavelength and CCD binning,
    # and ask the user to continue. Give the user option for choosing another file.
    while True:
        try:
            first_std_name=std_name[0][0].replace(raw_path,'').replace('[2,inherit=yes]','')
            print('')
            print("Selected STANDARD STAR file: {}".format(first_std_name))
            print('')
            answer = raw_input("Continue? [y/n] ")
            ccdsum_file = iraf.hselect("{}{}[2,inherit=yes]".format(raw_path,first_std_name),
                                        'Ccdsum', select_std, Stdout=1)[0]

            if answer == 'y':
                filename = first_std_name
                break
            if answer == 'n':

                print('')
                filename = raw_input("Type your selected file name: ")
                ccdsum_file = iraf.hselect("{}{}[2,inherit=yes]".format(raw_path,filename),
                                            'Ccdsum', select_std, Stdout=1)[0]
                break

            else:
                print('')
                print('Type y or n')
                print('')

        except (IndexError):
            print('')
            print("Check if you typed the correct name. ")

    # Append the selected file to the empty list.
    obj_std_name.append(filename)

    # Select the calibration files based on the previous selected parameters.
    print('')
    print("Selecting ARC, FLAT and BIAS...")

    # ARC
    arc_file=[]
    # Parameters for the IRAF task 'hselect'.
    select_arc_std = ("ObsType='ARC' && Ccdsum = {} "
                    "&& CentWave = {} ".format(ccdsum_file, wavelength))
    arc_file.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                                '$I', select_arc_std, Stdout=1))

    if arc_file == [[]]:
        print('')
        print("There is no ARC file matching the specified values")
        print('')

    else:
        print('')
        # Print the number of ARC files matching the specified values.
        print("It has been found {} ARC file(s) matching"
                "the specified values:".format(len(arc_file[0])))
        print('')
        arc_name=[]
        arc_name.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                                    '$I', select_arc_std, Stdout=1)) # File name.
        for j in range(len(arc_name[0])):
            # Print ARC names, CCD binning and title.
            # Remove '[2,inherit=yes]' and the 'raw_path' from their names.
            print(arc_name[0][j].replace('[2,inherit=yes]','').replace(raw_path,''))
        print('')

    # Select a file matching the values for central wavelength and CCD binning,
    # and ask the user to continue. Give the user option to choose another file.
    while True:
        try:
            first_arc_name=arc_name[0][0].replace(raw_path,'').replace('[2,inherit=yes]','')
            print('')
            print("Selected ARC file: {}".format(first_arc_name))
            print('')
            answer = raw_input("Continue? [y/n] ")

            if answer == 'y':
                filename = first_arc_name
                break
            if answer == 'n':

                print('')
                filename = raw_input("Type your selected file name: ")

                break
            else:
                print('')
                print('Type y or n')
                print('')

        except (IndexError):
            print('')
            print("Check if you typed the correct name. ")

    # Append the selected file to the empty list.
    arc_std_name.append(filename)

    # FLAT
    flat_file=[]
    # Parameters for the IRAF task 'hselect'.
    select_flat_std = ("ObsType='FLAT' && Ccdsum = {} && "
                        "CentWave = {}".format(ccdsum_file, wavelength))
    flat_file.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                        '$I', select_flat_std, Stdout=1))

    if flat_file == [[]]:
        print('')
        print("There is no FLAT file matching the specified values")
        print('')

    else:
        print('')
        # Print the number of FLAT files matching the specified values.
        print("It has been found {} FLAT file(s) matching "
                "the specified values:".format(len(flat_file[0])))
        print('')
        flat_name=[]
        flat_name.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                            '$I', select_flat_std, Stdout=1)) # File name.
        for j in range(len(flat_name[0])):
            # Print FLAT names, CCD binning and title.
            # Remove '[2,inherit=yes]' and the 'raw_path' from their names.
            print(flat_name[0][j].replace('[2,inherit=yes]','').replace(raw_path,''))

        print('')
    # Remove pre-existing FLAT list.
    if os.path.exists("flat_std.txt"):
        os.remove("flat_std.txt")

    # Select a file matching the values for central wavelength and CCD binning,
    # and ask the user to continue. Give the user option to choose another file.
    while True:
        try:
            first_flat_name=flat_name[0][0].replace(raw_path,'').replace('[2,inherit=yes]','')
            print('')
            print("Selected FLAT file: {}".format(first_flat_name))
            print('')
            answer = raw_input("Continue? [y/n] ")

            if answer == 'y':
                flat_std_list.append(first_flat_name)
                break
            if answer == 'n':

                print('')
                filename = raw_input("Type your selected file name: ")
                flat_std_list.append(filename)

                break
            else:
                print('')
                print('Type y or n')
                print('')
        except (IndexError):
            print('')
            print("Check if you typed the correct name. ")

    # Give the user option to add more FLAT files to the list.
    while True:
        try:
            print('')
            answer = raw_input('Do you wish to add more files? [y/n] ')

            if answer == "y":
                print('')
                filename = raw_input("Type your selected file name: ")
                flat_std_list.append(filename)

            if answer == "n":
                break

            else:
                print('')
                print("Type y or n")

        except (IndexError):
            print('')
            print("Check if you typed the correct name. ")

    # Create a '.txt' FLAT list.
    for j in range(len(flat_std_list)):
        flat_std_txt = open("flat_std.txt","a")
        flat_std_txt.write(flat_std_list[j])
        flat_std_txt.write("\n")
        flat_std_txt.close()

    # BIAS
    bias_file=[]
    # Parameters for the IRAF task 'hselect'.
    select_bias_std = 'ObsType="BIAS" && Ccdsum = {}'.format(ccdsum_file)
    bias_file.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                        '$I', select_bias_std, Stdout=1))

    if bias_file == [[]]:
        print('')
        print("There is no BIAS file matching the specified values")
        print('')

    else:
        print('')
        # Print the number of BIAS files matching the specified values.
        print("It has been found {} BIAS file(s) matching the"
                "specified value:".format(len(bias_file[0])))
        print('')
        bias_name=[]

        bias_name.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                            '$I', select_bias_std, Stdout=1))# File name.
        for j in range(len(bias_name[0])):
            # Print BIAS names, CCD binning and title.
            # Remove '[2,inherit=yes]' and the 'raw_path' from their names.
            print(bias_name[0][j].replace('[2,inherit=yes]','').replace(raw_path,''))

        print('')
    # Remove pre-existing BIAS list.
    if os.path.exists("bias_std.txt"):
        os.remove("bias_std.txt")

    # Select a file matching the values for central wavelength and CCD binning,
    # and ask the user to continue. Give the user option to choose another file.
    while True:
        try:
            first_bias_name=bias_name[0][0].replace(raw_path,'').replace('[2,inherit=yes]','')
            print('')
            print("Selected BIAS file: {}".format(first_bias_name))
            print('')
            answer = raw_input("Continue? [y/n] ")

            if answer == 'y':
                bias_std_list.append(first_bias_name)
                break
            if answer == 'n':

                print('')
                filename = raw_input("Type your selected file name: ")
                bias_std_list.append(filename)

                break
            else:
                print('')
                print('Type y or n')
                print('')
        except (IndexError):
            print('')
            print("Check if you typed the correct name. ")

    # Give the user option to add more BIAS files to the list.
    while True:
        try:
            print('')
            answer = raw_input('Do you wish to add more files? [y/n] ')

            if answer == "y":
                print('')
                filename = raw_input("Type your selected file name: ")
                bias_std_list.append(filename)

            if answer == "n":
                break

            else:
                print('')
                print("Type y or n")

        except (IndexError):
            print('')
            print("Check if you typed the correct name. ")

    # Create a '.txt' FLAT list.
    for j in range(len(bias_std_list)):
        bias_std_txt = open("bias_std.txt","a")
        bias_std_txt.write(bias_std_list[j])
        bias_std_txt.write("\n")
        bias_std_txt.close()

    # Ask the user to continue with the selected calibration files.
    while True:
        print('')
        answer = raw_input("Do you want to continue the data reduction"
                            "with the selected files [y/n]? ")
        if answer == "y":
            break

        if answer == "n":
            exit(0)

        else:
            print("Type y or n")

def selec_obj():
    """ Select a Science Object and its calibration files matching their
    central wavelength and CCD binning. """

    while True:
        try:
            print('')
            # Ask for a central wavelength value.
            wavelength = int(input("Type the central wavelength for the SCIENCE OBJECT: "))

            # Parameters for the IRAF task 'hselect'.
            select_obj = ("ObsType='OBJECT' && obsclass?='science' && CentWave = {}".format(wavelength))

            print('')
            # Print the selected parameters.
            print("Selecting " + select_obj)

            # Confirm the existence of files with the selected parameters.
            selected_files=[]
            selected_files.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                                    '$I', select_obj, Stdout=1))

            if selected_files == [[]]:
                print('')
                print("There is no file matching the specified value.")

            else:
                print('')
                # Print the number of SCIENCE OBJECT files matching the specified
                # values.
                print("It has been found {} SCIENCE OBJECT file(s)"
                        "matching the specified values:".format(len(selected_files[0])))
                print('')
                print(" Name \ CCDsum ")
                print('')

                obj_name=[]
                obj_ccdsum=[]
                obj_name.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                                '$I', select_obj, Stdout=1)) # File name.
                obj_ccdsum.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                                    '$Ccdsum', select_obj, Stdout=1)) # File CCD Binning.
                for j in range(len(obj_name[0])):
                    # Print SCIENCE OBJECT names, CCD binning and title.
                    # Remove '[2,inherit=yes]' and 'raw_path' from their names.
                    print(obj_name[0][j].replace('[2,inherit=yes]','').replace(raw_path,''),
                        obj_ccdsum[0][j])

                break

        except (NameError, SyntaxError,IndexError):
            print('')
            print("Check if you typed a correct central wavelength. ")

    # Select a file matching the values for central wavelength and CCD binning,
    # and ask the user to continue. Give the user option for choosing another file.
    while True:
        try:
            first_obj_name=obj_name[0][0].replace(raw_path,'').replace('[2,inherit=yes]','')
            print('')
            print("Selected SCIENCE OBJECT file: {}".format(first_obj_name))
            print('')
            answer = raw_input("Continue? [y/n] ")
            ccdsum_file = iraf.hselect("{}{}[2,inherit=yes]".format(raw_path,first_obj_name),
                                        'Ccdsum', select_obj, Stdout=1)[0]

            if answer == 'y':
                filename = first_obj_name
                break
            if answer == 'n':

                print('')
                filename = raw_input("Type your selected file name: ")
                ccdsum_file = iraf.hselect("{}{}[2,inherit=yes]".format(raw_path,filename),
                                            'Ccdsum', select_obj, Stdout=1)[0]
                break

            else:
                print('')
                print('Type y or n')
                print('')

        except (IndexError):
            print('')
            print("Check if you typed the correct name. ")

    # Append the selected file to the empty list.
    obj_sci_name.append(filename)

    # Select the calibration files based on the previous selected parameters.
    print('')
    print("Selecting ARC, FLAT and BIAS...")

    # ARC
    arc_file_obj=[]
    # Parameters for the IRAF task 'hselect'.
    select_arc_obj = ("ObsType='ARC' && Ccdsum = {} &&"
                        "CentWave = {}".format(ccdsum_file, wavelength))
    arc_file_obj.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                        '$I', select_arc_obj, Stdout=1))

    if arc_file_obj == [[]]:
        print('')
        print("There is no ARC file matching the specified values")
        print('')

    else:
        print('')
        # Print the number of ARC files matching the specified values.
        print("It has been found {} ARC file(s) matching the"
                "specified values:".format(len(arc_file_obj[0])))
        print('')
        arc_name_obj=[]
        arc_name_obj.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                            '$I', select_arc_obj, Stdout=1)) # File name.
        for j in range(len(arc_name_obj[0])):
            # Print ARC names, CCD binning and title.
            # Remove '[2,inherit=yes]' and the 'raw_path' from their names.
            print(arc_name_obj[0][j].replace('[2,inherit=yes]','').replace(raw_path,''))
        print('')

    # Select a file matching the values for central wavelength and CCD binning,
    # and ask the user to continue. Give the user option to choose another file.
    while True:
        try:
            first_arc_name=arc_name_obj[0][0].replace(raw_path,'').replace('[2,inherit=yes]','')
            print('')
            print("Selected ARC file: {}".format(first_arc_name))
            print('')
            answer = raw_input("Continue? [y/n] ")

            if answer == 'y':
                filename = first_arc_name
                break
            if answer == 'n':

                print('')
                filename = raw_input("Type your selected file name: ")

                break
            else:
                print('')
                print("Type y or n")
                print('')

        except (IndexError):
            print('')
            print("Check if you typed the correct name. ")

    # Append the selected file to the empty list.
    arc_sci_name.append(filename)

    # FLAT
    flat_file_obj=[]
    # Parameters for the IRAF task 'hselect'.
    select_flat_obj = ("ObsType='FLAT' && Ccdsum = {}"
                    "&& CentWave = {}".format(ccdsum_file, wavelength))
    flat_file_obj.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                        '$I', select_flat_obj, Stdout=1))

    if flat_file_obj == [[]]:
        print('')
        print("There is no FLAT file matching the specified values")
        print('')

    else:
        print('')
        # Print the number of FLAT files matching the specified values.
        print("It has been found {} FLAT file(s) matching the specified"
                    "values:".format(len(flat_file_obj[0])))
        print('')
        flat_name_obj=[]
        flat_name_obj.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                                '$I', select_flat_obj, Stdout=1)) # File name.
        for j in range(len(flat_name_obj[0])):
                # Print FLAT names, CCD binning and title.
                # Remove '[2,inherit=yes]' and the 'raw_path' from their names.
            print(flat_name_obj[0][j].replace('[2,inherit=yes]','').replace(raw_path,''))

        print('')
    # Remove pre-existing FLAT list.
    if os.path.exists("flat_obj.txt"):
        os.remove("flat_obj.txt")

    # Select a file matching the values for central wavelength and CCD binning,
    # and ask the user to continue. Give the user option to choose another file.
    while True:
        try:
            first_flat_name=flat_name_obj[0][0].replace(raw_path,'').replace('[2,inherit=yes]','')
            print('')
            print("Selected FLAT file: {}".format(first_flat_name))
            print('')
            answer = raw_input("Continue? [y/n] ")

            if answer == 'y':
                flat_obj_list.append(first_flat_name)
                break
            if answer == 'n':

                print('')
                filename = raw_input("Type your selected file name: ")
                flat_obj_list.append(filename)

                break
            else:
                print('')
                print("Type y or n")
                print('')
        except (IndexError):
            print('')
            print("Check if you typed the correct name. ")

    # Give the user option to add more FLAT files to the list.
    while True:
        try:
            print('')
            answer = raw_input('Do you wish to add more files? [y/n] ')

            if answer == "y":
                print('')
                filename = raw_input("Type your selected file name: ")
                flat_obj_list.append(filename)

            if answer == "n":
                break

            else:
                print('')
                print("Type y or n")

        except (IndexError):
            print('')
            print("Check if you typed the correct name. ")

    # Create a '.txt' FLAT list.
    for j in range(len(flat_obj_list)):
        flat_obj_txt = open("flat_obj.txt","a")
        flat_obj_txt.write(flat_obj_list[j])
        flat_obj_txt.write("\n")
        flat_obj_txt.close()

    # BIAS
    bias_file_obj=[]
    # Parameters for the IRAF task 'hselect'.
    select_bias_obj = 'ObsType="BIAS" && Ccdsum = {}'.format(ccdsum_file)
    bias_file_obj.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                            '$I', select_bias_obj, Stdout=1))

    if bias_file_obj == [[]]:
        print('')
        print("There is no BIAS file matching the specified values")
        print('')

    else:
        print('')
        # Print the number of BIAS files matching the specified values.
        print("It has been found {} BIAS file(s) matching the specified"
                "values:".format(len(bias_file_obj[0])))
        print('')
        bias_name_obj=[]

        bias_name_obj.append(iraf.hselect("{}*.fits[2,inherit=yes]".format(raw_path),
                                '$I', select_bias_obj, Stdout=1))

        for j in range(len(bias_name_obj[0])):
            # Print BIAS names, CCD binning and title.
            # Remove '[2,inherit=yes]' and the 'raw_path' from their names.
            print(bias_name_obj[0][j].replace('[2,inherit=yes]','').replace(raw_path,''))

        print('')
    # Remove pre-existing BIAS list.
    if os.path.exists("bias_obj.txt"):
        os.remove("bias_obj.txt")

    # Select a file matching the values for central wavelength and CCD binning,
    # and ask the user to continue. Give the user option to choose another file.
    while True:
        try:
            first_bias_name=bias_name_obj[0][0].replace(raw_path,'').replace('[2,inherit=yes]','')
            print('')
            print("Selected BIAS file: {}".format(first_bias_name))
            print('')
            answer = raw_input("Continue? [y/n] ")

            if answer == 'y':
                bias_obj_list.append(first_bias_name)
                break
            if answer == 'n':

                print('')
                filename = raw_input("Type your selected file name: ")
                bias_obj_list.append(filename)

                break
            else:
                print('')
                print("Type y or n")
                print('')
        except (IndexError):
            print('')
            print("Check if you typed the correct name. ")

    # Give the user option to add more BIAS files to the list.
    while True:
        try:
            print('')
            answer = raw_input('Do you wish to add more files? [y/n] ')

            if answer == "y":
                print('')
                filename = raw_input("Type your selected file name: ")
                bias_std_list.append(filename)

            if answer == "n":
                break

            else:
                print('')
                print "Type y or n"

        except (IndexError):
            print('')
            print("Check if you typed the correct name. ")

    # Create a '.txt' FLAT list.
    for j in range(len(bias_obj_list)):
        bias_obj_txt = open("bias_obj.txt","a")
        bias_obj_txt.write(bias_obj_list[j])
        bias_obj_txt.write("\n")
        bias_obj_txt.close()

    # Ask the user to continue with the selected calibration files.
    while True:
        print('')
        answer = raw_input("Do you want to continue the data reduction "
                            "with the selected files [y/n]? ")
        if answer == "y":
            break

        if answer == "n":
            exit(0)

        else:
            print("Type y or n")

# Reduction and calibration of STANDARD STAR files.
print "------------------------------"
print "# REDUCTION OF STANDARD STAR #"
print "------------------------------"

def std_gbias():
    """ Apply overscan correction and trim individual bias frames.
        Create Master Bias. Plot Master Bias and pixel counting. """

    print('# CREATING MASTER BIAS #')

    # Remove pre-existing Master Bias.
    if os.path.exists('Bias_std.fits'):
        os.remove('Bias_std.fits')

    gmos.gbias.unlearn() # Debug gbias.
    # Set the task parameters.
    biasFlags = {'rawpath':'raw', 'fl_over':'yes',
                'fl_trim':'yes', 'fl_vardq':'yes'}
    # Create Master Bias.
    gmos.gbias('@bias_std.txt', 'Bias_std.fits', **biasFlags) # IRAF task gbias.

    # Load Master Bias.
    obj=fits.open('Bias_std.fits')
    obj_data = obj[2].data
    obj_shape = obj_data.shape

    # Print Master Bias.
    fig = plt.figure(figsize=(14.0,4.0))
    for i in range(len(np.arange(0,12,1))):
        ax = plt.subplot(1, 12,i+1)
        plt.imshow(obj[i+1].data, origin='lower',cmap='afmhot',
                   vmin=np.percentile(obj[i+1].data,5),
                   vmax=np.percentile(obj[i+1].data,90), aspect='auto')
        if i == 0:
            ax.yaxis.set_visible(True)
            ax.set_ylabel('Position Along Slit', fontsize=14)
        else:
            ax.yaxis.set_visible(False)
    plt.tight_layout(w_pad=-0.9)
    plt.suptitle('Master BIAS', y=1.0, fontsize=14)
    plt.savefig('master-bias-std-{}.png'.format(obj_std_name[0]))

    plt.show()
    plt.clf()
    plt.close()

    # Print the pixel counting through a line cut.
    plt.figure(figsize=(16.0,8.0))
    for j in range(len(np.arange(0,12,1))):
        ax1 = plt.subplot(3, 12,j+1)
        ax1.set_ylim(min(obj[1].data[int(0.3*obj_shape[0]),1:obj_shape[1]]),
                        max(obj[1].data[int(0.3*obj_shape[0]),1:obj_shape[1]]))
        ax1.plot(np.arange(1,obj_shape[1],1),
                    obj[j+1].data[int(0.3*obj_shape[0]),1:obj_shape[1]],linewidth=0.5)

        ax2 = plt.subplot(3, 12,12+j+1)
        ax2.set_ylim(min(obj[1].data[int(0.5*obj_shape[0]),1:obj_shape[1]]),
                        max(obj[1].data[int(0.5*obj_shape[0]),1:obj_shape[1]]))
        ax2.plot(np.arange(1,obj_shape[1],1),
                    obj[j+1].data[int(0.5*obj_shape[0]),1:obj_shape[1]],linewidth=0.5)

        ax3 = plt.subplot(3, 12, 24+j+1)
        ax3.set_ylim(min(obj[1].data[int(0.7*obj_shape[0]),1:obj_shape[1]]),
                        max(obj[1].data[int(0.7*obj_shape[0]),1:obj_shape[1]]))
        ax3.plot(np.arange(1,obj_shape[1],1),
                    obj[j+1].data[int(0.7*obj_shape[0]),1:obj_shape[1]],linewidth=0.5)
        if j == 0:
            ax1.yaxis.set_visible(True)
            ax1.set_ylabel('Counts [row={}]'.format(int(0.3*obj_shape[0])), fontsize=14)
            ax2.yaxis.set_visible(True)
            ax2.set_ylabel('Counts [row={}]'.format(int(0.5*obj_shape[0])), fontsize=14)
            ax3.yaxis.set_visible(True)
            ax3.set_ylabel('Counts [row={}]'.format(int(0.7*obj_shape[0])), fontsize=14)
        else:
            ax1.yaxis.set_visible(False)
            ax2.yaxis.set_visible(False)
            ax3.yaxis.set_visible(False)
    plt.tight_layout(w_pad=-0.9)
    plt.suptitle('Pixel Counting',y=1.0, fontsize=14)
    plt.savefig('pixel-counting-bias-std-{}.png'.format(obj_std_name[0]))
    plt.show()
    plt.close()

def std_reduc_arc():
    """ Apply overscan correction and mosaic arc frames. """

    print('# REDUCING ARC LAMP #')

    # Remove pre-existing calibrated files.
    if os.path.exists('gs{}'.format(arc_std_name[0])):
        os.remove('gs{}'.format(arc_std_name[0]))

    gmos.gsreduce.unlearn() # Debug gsreduce.
    # Set the task parameters.
    gsreduceFlags1={'rawpath':'raw', 'fl_bias':'yes',
                    'fl_flat':'no', 'fl_over':'yes',
                    'bias':'Bias_std', 'fl_gmos':'yes'}
    # Reduce arc frames.
    gmos.gsreduce(str(arc_std_name[0]), **gsreduceFlags1) # IRAF task gsreduce.

def std_wavelength_arc():
    """ Create a wavelength solution based on arc frames.
        Print the difference of the calculated and correct wavelength values
        for the estimated lines."""

    print('# CALIBRATING WAVELENGTH #')

    # Remove pre-existing wavelength solution files on database directory.
    if os.path.exists('database/idgs{}_001'.format(arc_std_name[0].replace('.fits',''))):
        os.remove('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')))

    # Load reduced arc frame.
    obj=fits.open('gs{}'.format(arc_std_name[0]))
    obj_data = obj[2].data
    arc_shape = obj_data.shape

    gmos.gswavelength.unlearn() # Debug gswavelength.
    # Set the task parameters.
    gswavelengthFlags={'nsum':str(arc_shape[0]/3), 'step':str(arc_shape[0]/3),
                        'fwidth':'7', 'gsigma':'1.5','cradius':'12',
                        'minsep':'7', 'order':'6','fl_inter':'no'}
    # Create wavelength solution.
    gmos.gswavelength('gs{}'.format(arc_std_name[0]), **gswavelengthFlags) # IRAF task gswavelength.

    # Read wavelength solution file on database directory.
    # Autoidentify.
    # Number of calculated features.
    number_of_features_auto = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')),
                                            skip_header=6, usecols=1, max_rows=1, invalid_raise=False)
    # Number of calculated coefficients.
    number_of_coefficients_auto = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')),
                                            skip_header=7+int(number_of_features_auto)+8, usecols=1,
                                                max_rows=1, invalid_raise=False)
    # gswavelength flags to discard outlier values.
    wave_flag_auto = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')), skip_header=7,
                                usecols=5, max_rows=int(number_of_features_auto), invalid_raise=False)
    # Row number.
    wave_auto_col_0 = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')), skip_header=7,
                                usecols=0, max_rows=int(number_of_features_auto), invalid_raise=False)
    # Corrected line wavelength.
    wave_auto_col_1  = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')), skip_header=7,
                                usecols=1, max_rows=int(number_of_features_auto), invalid_raise=False)
    # Calculated line wavelength.
    wave_auto_col_2  = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')), skip_header=7,
                                usecols=2, max_rows=int(number_of_features_auto), invalid_raise=False)

    # Reidentify.
    # Number of calculated features.
    number_of_features_re1 = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')),
                             skip_header=7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)+7,
                                        usecols=1, max_rows=1, invalid_raise=False)

    number_of_coefficients_re1 = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')),
           skip_header=7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)+8+int(number_of_features_re1)+8,
                                        usecols=1, max_rows=1, invalid_raise=False)

    # gswavelength flags to discard outlier values.
    wave_flag_re1 = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')),
                                skip_header=7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)+8,
                                usecols=5, max_rows=int(number_of_features_re1), invalid_raise=False)
    # Row number.
    wave_re1_col_0 = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')),
                                skip_header=7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)+8, usecols=0,
                                max_rows=int(number_of_features_re1), invalid_raise=False)
    # Corrected line wavelength.
    wave_re1_col_1 = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')),
                                skip_header=7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)+8, usecols=1,
                                max_rows=int(number_of_features_re1), invalid_raise=False)
    # Calculated line wavelength.
    wave_re1_col_2 = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')),
                                skip_header=7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)+8, usecols=2,
                                max_rows=int(number_of_features_re1), invalid_raise=False)

    # Reidentify.
    # Number of calculated features.

    number_of_features_re2 = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')),
                                        skip_header=(7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)
                                        +8+int(number_of_features_re1)+9+int(number_of_coefficients_re1)+7),
                                           usecols=1, max_rows=1, invalid_raise=False)

    # gswavelength flags to discard outlier values.
    wave_flag_re2 = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')),
                                skip_header=(7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)
                                        +8+int(number_of_features_re1)+9+int(number_of_coefficients_re1)+8),
                                  usecols=5, max_rows=int(number_of_features_re2), invalid_raise=False)
    # Row number.
    wave_re2_col_0 = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')),
                                skip_header=(7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)
                                        +8+int(number_of_features_re1)+9+int(number_of_coefficients_re1)+8),
                                  usecols=0, max_rows=int(number_of_features_re2), invalid_raise=False)
    # Corrected line wavelength.
    wave_re2_col_1 = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')),
                                skip_header=(7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)
                                        +8+int(number_of_features_re1)+9+int(number_of_coefficients_re1)+8),
                                  usecols=1, max_rows=int(number_of_features_re2), invalid_raise=False)
    # Calculated line wavelength.
    wave_re2_col_2 = np.genfromtxt('database/idgs{}_001'.format(arc_std_name[0].replace('.fits','')),
                                skip_header=(7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)
                                        +8+int(number_of_features_re1)+9+int(number_of_coefficients_re1)+8),
                                  usecols=2, max_rows=int(number_of_features_re2), invalid_raise=False)

    # gswavelength flags
    flag_auto = np.where(wave_flag_auto[0:,] == 1) # Autoidentify.
    flag_re1 = np.where(wave_flag_re1[0:,] == 1) # Reidentify.
    flag_re2 = np.where(wave_flag_re2[0:,] == 1) # Reidentify.

    # RMS estimate.

    # Autoidentify.
    rows_auto = wave_auto_col_0[0:,][flag_auto]
    delta_lambda_auto = wave_auto_col_2[0:,][flag_auto] - wave_auto_col_1[0:,][flag_auto]
    rms_auto = np.sqrt(np.sum(delta_lambda_auto**2) / len(rows_auto))

    print('[AUTOIDENTIFY] RMS = ', rms_auto)

    hig_than_rms_auto=[] # Values higher than RMS.
    for l in range(len(delta_lambda_auto)):
        if np.abs(delta_lambda_auto[l]) > rms_auto:
            hig_than_rms_auto.append( wave_auto_col_2[0:,][flag_auto][l])
    # Print number of lines with values diverging from the correct value
    # whith a difference higher thant the RMS.
    print("[AUTOIDENTIFY] There are {} identified lines diverging from the"
            " observed value with differences higher than the RMS :".format(len(hig_than_rms_auto)), hig_than_rms_auto)

     # Reidentify.
    rows_re1 = wave_re1_col_0[0:,][flag_re1]
    delta_lambda_re1 = wave_re1_col_2[0:,][flag_re1] - wave_re1_col_1[0:,][flag_re1]
    rms_re1 = np.sqrt(np.sum(delta_lambda_re1**2) / len(rows_re1))

    print('[REIDENTIFY] RMS = ', rms_re1)

    hig_than_rms_re1=[] # Values higher than RMS.
    for l in range(len(delta_lambda_re1)):
        if np.abs(delta_lambda_re1[l]) > rms_re1:
            hig_than_rms_re1.append(wave_re1_col_2[0:,][flag_re1][l])
    # Print number of lines with values diverging from the correct value
    # whith a difference higher thant the RMS.
    print("[REIDENTIFY] There are {} identified lines diverging from the"
            " observed value with differences higher than the RMS :".format(len(hig_than_rms_re1)), hig_than_rms_re1)

    # Reidentify.
    rows_re2 = wave_re2_col_0[0:,][flag_re2]
    delta_lambda_re2 = wave_re2_col_2[0:,][flag_re2] - wave_re2_col_1[0:,][flag_re2]
    rms_re2 = np.sqrt(np.sum(delta_lambda_re2**2) / len(rows_re2))

    print('[REIDENTIFY] RMS = ', rms_re2)

    hig_than_rms_re2=[]  # Values higher than RMS.
    for l in range(len(delta_lambda_re2)):
        if np.abs(delta_lambda_re2[l]) > rms_re2:
            hig_than_rms_re2.append(wave_re2_col_2[0:,][flag_re2][l])
    # Print number of lines with values diverging from the correct value
    # whith a difference higher thant the RMS.
    print("[REIDENTIFY] There are {} identified lines diverging from the"
            " observed value with differences higher than the RMS :".format(len(hig_than_rms_re2)), hig_than_rms_re2)

    # Print the difference of the calculated and correct wavelength values
    # for the estimated lines.
    # Autoidentify.
    fig = plt.figure(figsize=(14.0,6.0))
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twiny()
    ax3 = ax1.twiny()
    ax4 = ax1.twiny()
    ax1.scatter(rows_auto,np.abs(delta_lambda_auto), color='white' )
    ax2.scatter(wave_auto_col_2[0:,][flag_auto], np.abs(delta_lambda_auto), color='coral')
    ax2.invert_xaxis()
    plt.title('Autoidentify', y=1.10, fontsize=14)
    ax2.set_xlabel(r'$\lambda_{identified} \ [\AA]$', fontsize=14)
    ax1.set_xlabel('Pixel position', fontsize=14)
    ax1.set_ylabel(r'|$\lambda_{identified} - \lambda_{fitted}| \ [\AA]$', fontsize=14)
    ax3.axhline(y=0.2, linestyle='--')
    ax3.xaxis.set_visible(False)
    ax4.axhline(y=rms_auto, linestyle=':', label='RMS = {}'.format(rms_auto))
    ax4.xaxis.set_visible(False)
    plt.tight_layout(w_pad=-0.9)
    ax4.legend()
    plt.savefig('autoidentify_std-{}.png'.format(obj_std_name[0]))
    plt.show()
    plt.close()

    # Reidentify.
    fig = plt.figure(figsize=(14.0,6.0))
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twiny()
    ax3 = ax1.twiny()
    ax4 = ax1.twiny()
    ax1.scatter(rows_re1,np.abs(delta_lambda_re1), color='white' )
    ax2.scatter(wave_re1_col_2[0:,][flag_re1] ,np.abs(delta_lambda_re1), color='coral')
    ax2.invert_xaxis()
    plt.title('Reidentify', y=1.10, fontsize=14)
    ax2.set_xlabel(r'$\lambda_{identified} \ [\AA]$', fontsize=14)
    ax1.set_xlabel('Pixel position', fontsize=14)
    ax1.set_ylabel(r'|$\lambda_{identified} - \lambda_{fitted}| \ [\AA]$', fontsize=14)
    ax3.axhline(y=0.2, linestyle='--')
    ax3.xaxis.set_visible(False)
    ax4.axhline(y=rms_re1, linestyle=':', label='RMS = {}'.format(rms_re1))
    ax4.xaxis.set_visible(False)
    plt.tight_layout(w_pad=-0.9)
    ax4.legend()
    plt.show()
    plt.close()

    # Reidentify.
    fig = plt.figure(figsize=(14.0,6.0))
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twiny()
    ax3 = ax1.twiny()
    ax4 = ax1.twiny()
    ax1.scatter(rows_re2,np.abs(delta_lambda_re2), color='white' )
    ax2.scatter(wave_re2_col_2[0:,][flag_re2] ,np.abs(delta_lambda_re2), color='coral')
    ax2.invert_xaxis()
    plt.title('Reidentify', y=1.10, fontsize=14)
    ax2.set_xlabel(r'$\lambda_{identified} \ [\AA]$', fontsize=14)
    ax1.set_xlabel('Pixel position', fontsize=14)
    ax1.set_ylabel(r'|$\lambda_{identified} - \lambda_{fitted}| \ [\AA]$', fontsize=14)
    ax3.axhline(y=0.2, linestyle='--')
    ax3.xaxis.set_visible(False)
    ax4.axhline(y=rms_re2, linestyle=':', label='RMS = {}'.format(rms_re2))
    ax4.xaxis.set_visible(False)
    plt.tight_layout(w_pad=-0.9)
    ax4.legend()
    plt.show()
    plt.close()

def std_transf_arc():
    """ Transform arc files. """

    print('# TRANSFORMING ARC FILES #')

    # Remove pre-existing transformed files.
    if os.path.exists('tgs{}'.format(arc_std_name[0])):
        os.remove('tgs{}'.format(arc_std_name[0]))

    gmos.gstransform.unlearn() # Debug gstransform.
    # Set the task parameters.
    gstransformFlags={'wavtranam':'gs{}'.format(arc_std_name[0])}
    # Transform arc files.
    gmos.gstransform('gs{}'.format(arc_std_name[0]), **gstransformFlags) # IRAF task gstransform.

def std_reduc_flat():
    """ Subtract bias from individual flat frames. """

    print('# REDUCING RAW FLATS #')

    # Open individual flat frames.
    f = open('flat_std.txt', 'r')
    for flatfile in f:
        # Remove pre-existing processed files.
        if os.path.exists('gs{}'.format(flatfile.replace('\n',''))):
            os.remove('gs{}'.format(flatfile.replace('\n','')))

        gmos.gsreduce.unlearn() # Debug gsreduce.
        # Set the task parameters.
        gsreduceFlags={'rawpath':'raw', 'fl_bias':'yes',
                        'fl_flat':'no', 'fl_fixpix':'no',
                        'bias':'Bias_std.fits','fl_gmos':'no',
                        'fl_gsappwave':'no', 'fl_cut':'no'}
        # Reduce flat files.
        gmos.gsreduce(str(flatfile.replace('\n','')), **gsreduceFlags) # IRAF task gsreduce.
    f.close()

def std_qecorr_flat():
    """ Apply quantum efficiency correction to individual
        flat frames. """

    print('# QUANTUM-CORRECTING FLAT#')

    # Open individual flat frames.
    f = open('flat_std.txt', 'r')
    for flatfile in f:
        # Remove pre-existing processed files.
        if os.path.exists('qgs{}'.format(flatfile.replace('\n',''))):
            os.remove('qgs{}'.format(flatfile.replace('\n','')))

        gmos.gqecorr.unlearn() # Debug gqecorr.
        # Set the task parameters.
        qecorrFlags= {'refimage':'gs{}'.format(arc_std_name[0]),
                    'fl_keep':'yes'}
        # Apply quantum efficiency correction.
        gmos.gqecorr('gs{}'.format(flatfile.replace('\n','')), **qecorrFlags) # IRAF task gqecorr.
    f.close()

def std_gmosaic_flat():
    """ Mosaic individual flat frames. """

    print('# MOSAIC FLAT#')

    # Remove pre-existing list.
    if os.path.exists("mqgsflat_std.txt"):
        os.remove("mqgsflat_std.txt")

    # Open individual flat frames.
    f = open('flat_std.txt', 'r')
    for flatfile in f:
        # Remove pre-existing processed files.
        if os.path.exists('mqgs{}'.format(flatfile.replace('\n',''))):
            os.remove('mqgs{}'.format(flatfile.replace('\n','')))

        gmos.gmosaic.unlearn() # Debug gmosaic.
        # Set the task parameters.
        gmosaicFlags= {'fl_fixpix':'yes'}
        # Mosaic flat frames.
        gmos.gmosaic('qgs{}'.format(flatfile.replace('\n','')), **gmosaicFlags) # IRAF task gmosaic.

        # Write name of processed files on list.
        mqgsflat = open("mqgsflat_std.txt","a")
        mqgsflat.write('mqgs{}'.format(flatfile.replace('\n','')))
        mqgsflat.write("\n")
        mqgsflat.close()

    f.close()

def std_masterflat():
    """ Trim individual flat frames and create Master Flat.
        Print Master Flat and pixel counting. """

    print('# CREATING MASTER FLAT #')

    # Remove pre-existing Master Flat.
    if os.path.exists('qFlat_std.fits'):
        os.remove('qFlat_std.fits')

    gmos.gsflat.unlearn() # Debug gsflat.
    # Set the task parameters.
    flatFlags = {'fl_bias':'no', 'order':'29',
                'fl_over':'no', 'fl_trim':'no',
                'fl_usegrad':'yes'}
    # Create Master Flat.
    gmos.gsflat('@mqgsflat_std.txt', 'qFlat_std.fits', **flatFlags) # IRAF task gsflat.

    # Load Master Flat.
    obj=fits.open('qFlat_std.fits')
    obj_data = obj[2].data
    obj_shape = obj_data.shape

    # Plot Master Flat.
    plt.figure(figsize=(12.0,4.0))
    plt.imshow(obj[2].data, origin='lower',cmap='afmhot',
               vmin=np.percentile(obj[2].data,5),
               vmax=np.percentile(obj[2].data,90), aspect='auto')
    plt.ylabel('Position Along Slit', fontsize=14)
    plt.xlabel('Dispersion Axis', fontsize=14)
    plt.tight_layout(w_pad=-0.9)
    plt.suptitle('Master FLAT', y=1.0, fontsize=14)
    plt.savefig('master-flat-std-{}.png'.format(obj_std_name[0]))
    plt.show()
    plt.clf()
    plt.close()

    # Print the pixel counting through a line cut.
    plt.figure(figsize=(16.0,8.0))
    ax1 = plt.subplot(3, 1, 1)
    ax1.set_ylim(min(obj[2].data[int(0.3*obj_shape[0]),1:obj_shape[1]]),
                    max(obj[2].data[int(0.3*obj_shape[0]),1:obj_shape[1]]))
    ax1.set_ylabel('Counts [row={}]'.format(int(0.3*obj_shape[0])), fontsize=14)
    ax1.plot(np.arange(1,obj_shape[1],1),
                obj[2].data[int(0.3*obj_shape[0]),1:obj_shape[1]],linewidth=0.5)

    ax2 = plt.subplot(3, 1, 2)
    ax2.set_ylim(min(obj[2].data[int(0.5*obj_shape[0]),1:obj_shape[1]]),
                    max(obj[2].data[int(0.5*obj_shape[0]),1:obj_shape[1]]))
    ax2.set_ylabel('Counts [row={}]'.format(int(0.5*obj_shape[0])), fontsize=14)
    ax2.plot(np.arange(1,obj_shape[1],1),
                obj[2].data[int(0.5*obj_shape[0]),1:obj_shape[1]],linewidth=0.5)
    ax3 = plt.subplot(3, 1, 3)
    ax3.set_ylim(min(obj[2].data[int(0.7*obj_shape[0]),1:obj_shape[1]]),
                    max(obj[2].data[int(0.7*obj_shape[0]),1:obj_shape[1]]))
    ax3.set_ylabel('Counts [row={}]'.format(int(0.7*obj_shape[0])), fontsize=14)
    ax3.plot(np.arange(1,obj_shape[1],1),
                obj[2].data[int(0.7*obj_shape[0]),1:obj_shape[1]],linewidth=0.5)
    ax3.set_xlabel('Dispersion Axis', fontsize=14)
    plt.tight_layout(w_pad=-0.9)
    plt.suptitle('Pixel Counting',y=1.0, fontsize=14)
    plt.savefig('pixel-counting-flat-std-{}.png'.format(obj_std_name[0]))
    plt.show()
    plt.close()

def std_reduc1_std():
    """ Subtract bias, apply overscan and cosmic ray correction
        to standard star frames. """

    print('# 1st REDUCTION #')

    # Remove pre-existing processed files.
    if os.path.exists('gs{}'.format(obj_std_name[0])):
        os.remove('gs{}'.format(obj_std_name[0]))

    gmos.gsreduce.unlearn() # Debug gsreduce.
    # Task parameters.
    gsreduceFlags={'rawpath':'raw','fl_gmos':'no', 'fl_fixpix':'no',
                    'fl_flat':'no', 'fl_vardq':'yes',
                    'fl_fulldq':'yes', 'fl_bias':'yes',
                    'bias':'Bias_std', 'fl_inter':'no',
                    'fl_cut':'no', 'fl_gsappwave':'no',
                    'fl_over':'yes', 'fl_crspec':'yes'}
    # Reduce standard star files.
    gmos.gsreduce(str(obj_std_name[0]), **gsreduceFlags) # IRAF task gsreduce.

def std_gemfix_std():
    """ Improve cosmic ray and bad pixel correction.
        Print raw and corrected files for comparison. """

    print('# GEMFIX #')

    # Remove pre-existing processed files.
    if os.path.exists('gemgs{}'.format(obj_std_name[0])):
        os.remove('gemgs{}'.format(obj_std_name[0]))
    if os.path.exists('copy_gemgs{}'.format(obj_std_name[0])):
        os.remove('copy_gemgs{}'.format(obj_std_name[0]))

    gemini.gemfix.unlearn() # Debug gemfix.
    # Task parameters.
    gemfixFlags={'outimages':'gemgs{}'.format(obj_std_name[0]),
                    'method':'fixpix', 'bitmask':'8'}
    # Fix bad pixels.
    gemini.gemfix('gs{}'.format(obj_std_name[0]), **gemfixFlags) # IRAF task gemfix.

    # Load raw files.
    obj=fits.open('raw/{}'.format(obj_std_name[0]))
    obj_data = obj[2].data
    obj_shape = obj_data.shape

    # Load processed files.
    gemobj=fits.open('gemgs{}'.format(obj_std_name[0]))
    gemobj_data = gemobj[2].data
    gemobj_shape = gemobj_data.shape

    # Create copy of processed file.
    copy_gemobj = fits.HDUList([gemobj[0]])
    for n in np.arange(2,37,3):
        copy_gemobj.append(gemobj[n])
    copy_gemobj.writeto('copy_gemgs{}'.format(obj_std_name[0]))
    new_gemobj = fits.open('copy_gemgs{}'.format(obj_std_name[0]))
    gemobj_data = gemobj[2].data
    gemobj_shape = gemobj_data.shape

    # Print raw and corrected files.
    plt.figure(figsize=(16.0,8.0))
    for i in range(len(np.arange(0,12,1))):
        ax1 = plt.subplot(2,12,i+1)
        ax1.imshow(obj[i+1].data, origin='lower',cmap='afmhot',
                   vmin=np.percentile(obj[i+1].data,5),
                   vmax=np.percentile(obj[i+1].data,90), aspect='auto')
        ax2 = plt.subplot(2,12,12+i+1)
        ax2.imshow(new_gemobj[i+1].data, origin='lower',cmap='afmhot',
                   vmin=np.percentile(new_gemobj[i+1].data,5),
                   vmax=np.percentile(new_gemobj[i+1].data,90), aspect='auto')
        if i == 0:
            ax1.yaxis.set_visible(True)
            ax1.set_ylabel('Position Along Slit', fontsize=14)
            ax2.yaxis.set_visible(True)
            ax2.set_ylabel('Position Along Slit', fontsize=14)
        else:
            ax1.yaxis.set_visible(False)
            ax2.yaxis.set_visible(False)
    plt.tight_layout(w_pad=-0.9)
    plt.suptitle('Pre- and Post- Cosmic Ray Rejection', y=1.0, fontsize=14)
    plt.savefig('gemfix_std-{}.png'.format(obj_std_name[0]))
    plt.show()
    plt.clf()
    plt.close()

def std_qecorr_std():
    """ Apply quantum efficiency correction to standard
        star frames. """

    print('# QUANTUM-CORRECTING #')

    # Remove pre-existing processed files.
    if os.path.exists('qgemgs{}'.format(obj_std_name[0])):
        os.remove('qgemgs{}'.format(obj_std_name[0]))

    # Open list of individual flat frames.
    flatfile_list=[]
    f = open('flat_std.txt', 'r')
    for flatfile in f:
        flatfile_list.append(flatfile)
    f.close()

    gmos.gqecorr.unlearn() # Debug gqecorr.
    # Task parameters
    qecorrFlags= {'refimage':'gs{}'.format(arc_std_name[0]),
                    'corrima':'qgs{}'.format(flatfile_list[0].replace('\n',''))}
    # Apply quantum efficiency correction.
    gmos.gqecorr('gemgs{}'.format(obj_std_name[0]), **qecorrFlags) # IRAF task gqecorr.

def std_reduc2_std():
    """ Apply flat field correction to standard star frames. """

    print('# 2nd REDUCTION #')

    # Remove pre-existing processed files.
    if os.path.exists('gsqgemgs{}'.format(obj_std_name[0])):
        os.remove('gsqgemgs{}'.format(obj_std_name[0]))

    gmos.gsreduce.unlearn() # Debug gsreduce.
    # Task parameters.
    gsreduceFlags={'fl_bias':'no', 'fl_flat':'yes',
                     'fl_over':'no', 'flat':'qFlat_std',
                    'fl_trim':'no'}
    # Apply flat correction.
    gmos.gsreduce('qgemgs{}'.format(obj_std_name[0]), **gsreduceFlags) # IRAF task gsreduce.

def std_badcolumn_std():
    """ Print standard star frame for bad column checking.
        Interpolate bad columns. """

    print('# BAD COLUMN CHECKING #')

    # Remove pre-existing processed files.
    if os.path.exists('bcgsqgemgs{}'.format(obj_std_name[0])):
        os.remove('bcgsqgemgs{}'.format(obj_std_name[0]))
    # Create copy of science object file to apply bad column correction.
    iraf.copy('gsqgemgs{}'.format(obj_std_name[0]), 'bcgsqgemgs{}'.format(obj_std_name[0]))
    # Load copy.
    obj=fits.open('bcgsqgemgs{}'.format(obj_std_name[0]))

    # Check if a bad column mask is already available in the directory.
    if os.path.exists("maskbadcol.txt"):
        while True:
            try:
                print('')
                answer = raw_input("The file 'maskbadcol.txt' is available in this directory. "
                                    " Do you wish to apply this mask to your spectrum? (y/n) ")
                if answer=='y':
                    # Remove pre-existing mask.
                    if os.path.exists("maskbadcol.pl"):
                        os.remove("maskbadcol.pl")

                    # Create mask based on coordinates text file.
                    iraf.text2mask('maskbadcol.txt', 'maskbadcol.pl',
                                    obj[2].shape[1], obj[2].shape[0]) # IRAF task 'text2mask'.

                    # Interpolate bad columns using mask.
                    iraf.fixpix('bcgsqgemgs{}[2]'.format(obj_std_name[0]),
                                    'maskbadcol.pl', linterp='1,2,3,4') # IRAF task 'fixpix'.
                    break

                if answer=='n':
                    break

                else:
                    print('Please, type y or n ')

            except(NameError, SyntaxError,IndexError):
                    print('')
                    print("Check if you typed a correct line number. ")

    # Select a line in the science object frame and print the pixel counting
    # through the line for bad column checking.
    while True:
        try:
            print('')
            # Selected line.
            line = int(input('Choose a line for bad column checking: ' ))
            print('')

            xaxis=np.arange(1, obj[2].data.shape[1],1)
            yaxis=obj[2].data[line,1:obj[2].data.shape[1]]

            # Print science object frame and pixel counting
            # through the selected line.
            plt.figure(figsize=(16.0,8.0))
            plt.figure(figsize=(16.0,8.0))
            ax1=plt.subplot(211)
            ax1.imshow(obj[2].data, origin='lower',cmap='afmhot',
                           vmin=np.percentile(obj[2].data,1),
                           vmax=np.percentile(obj[2].data,99), aspect='auto')
            ax1.axhline(y=line, linestyle='--', color='red',linewidth=2., alpha=0.7)
            ax1.set_ylabel('Position Along Slit', fontsize=14)
            ax2=plt.subplot(212)
            ax2.plot(xaxis, yaxis, color='red' )
            ax2.set_xlim(left=np.min(xaxis), right=np.max(xaxis))
            ax2.set_ylabel('Counts', fontsize=14)
            ax2.set_xlabel('Dispersion Axis', fontsize=14)
            plt.show()

            answer = raw_input('Do you wish to select another line? (y/n) ')

            if answer=='n':
                break
            if answer=='y':
                print('')
            else:
                print('Please, type y or n ')

        except(NameError, SyntaxError,IndexError):
                print('')
                print("Check if you typed a correct line number. ")

    # Select the inital and final position along the x-axis of
    # the columns to interpolate.
    # Create a mask and interpolate bad column.
    while True:
        try:
            print('')
            answer2 = raw_input('Do you wish to interpolate a bad column? (y/n) ')
            print('')

            if answer2=='n':
                break
            if answer2=='y':

                while True:
                    try:
                        print('')
                        # Inital x position of the bad column.
                        x1 = int(input('Select a column to interpolate (x min): ' ))
                        print('')
                        # Final x position of the bad column.
                        x2 = int(input('Select a column to interpolate (x max): ' ))

                        # Create text file with the column coordinates.
                        bias_obj_txt = open("maskbadcol.txt","a")
                        bias_obj_txt.write('{} {} 1 {}'.format(x1, x2, obj[2].shape[0]))
                        bias_obj_txt.write("\n")
                        bias_obj_txt.close()

                        # Remove pre-existing mask.
                        if os.path.exists("maskbadcol.pl"):
                            os.remove("maskbadcol.pl")

                        # Create mask based on coordinates text file.
                        iraf.text2mask('maskbadcol.txt', 'maskbadcol.pl',
                                        obj[2].shape[1], obj[2].shape[0]) # IRAF task 'text2mask'.

                        # Interpolate bad columns using mask.
                        iraf.fixpix('bcgsqgemgs{}[2]'.format(obj_std_name[0]),
                                        'maskbadcol.pl', linterp='1,2,3,4') # IRAF task 'fixpix'.

                        # Print corrected science object frame and pixel counting
                        # through the selected line.
                        obj2=fits.open('bcgsqgemgs{}'.format(obj_std_name[0]))
                        xaxis=np.arange(1, obj[2].data.shape[1],1)
                        yaxis=obj[2].data[line,1:obj[2].data.shape[1]]
                        plt.figure(figsize=(16.0,8.0))
                        ax1=plt.subplot(211)
                        ax1.imshow(obj[2].data, origin='lower',cmap='afmhot',
                                   vmin=np.percentile(obj[2].data,1),
                                   vmax=np.percentile(obj[2].data,99), aspect='auto')
                        ax1.axhline(y=line, linestyle='--', color='red',linewidth=2., alpha=0.7)
                        ax1.set_ylabel('Position Along Slit', fontsize=14)
                        ax2=plt.subplot(212)
                        ax2.plot(xaxis, yaxis, color='red' )
                        ax2.set_xlim(left=np.min(xaxis), right=np.max(xaxis))
                        ax2.set_ylabel('Counts', fontsize=14)
                        ax2.set_xlabel('Dispersion Axis', fontsize=14)
                        plt.show()

                        print('')
                        answer3 = raw_input('Do you wish to interpolate another bad column? (y/n) ' )

                        if answer3=='n':
                            break
                        if answer3=='y':
                            print('')
                        else:
                            print('Please, type y or n ')

                    except(NameError, SyntaxError,IndexError):
                            print('')
                            print("Check if you typed a correct line number. ")
                break
            else:
                print('Please, type y or n ')

        except(NameError, SyntaxError,IndexError):
                print('')
                print("Check if you typed a correct line number. ")

def std_transf_std():
    """ Transform standard star frame. """

    print('# TRANSFORMING STANDARD STAR #')

    # Remove pre-existing processed files.
    if os.path.exists('tbcgsqgemgs{}'.format(obj_std_name[0])):
        os.remove('tbcgsqgemgs{}'.format(obj_std_name[0]))

    gmos.gstransform.unlearn() # Debug gstransform.
    # Task parameters.
    gstransformFlags={'wavtranam':'gs{}'.format(arc_std_name[0]),
                    'fl_vardq':'yes'}
    # Transform spectrum.
    gmos.gstransform('bcgsqgemgs{}'.format(obj_std_name[0]), **gstransformFlags) # IRAF task gstransform.

def std_sky_sub_std():
    """ Subtract sky background from standard star frame.
        Print raw and sky subtracted frames for comparison. """

    print('# SKY-SUBTRACTING #')

    # Remove pre-existing processed files.
    if os.path.exists('stbcgsqgemgs{}'.format(obj_std_name[0])):
        os.remove('stbcgsqgemgs{}'.format(obj_std_name[0]))

    gmos.gsskysub.unlearn() # Debug gsskysub.
    # Task parameters.
    gsskysubFlags={'fl_int':'no'}
    # Subtract sky background.
    gmos.gsskysub('tbcgsqgemgs{}'.format(obj_std_name[0]), **gsskysubFlags) # IRAF task gsskysub.

    # Print frames with and without sky correction.
    obj=fits.open('tbcgsqgemgs{}'.format(obj_std_name[0]))
    subobj=fits.open('stbcgsqgemgs{}'.format(obj_std_name[0]))
    obj_data = obj[2].data
    subobj_data = subobj[2].data
    obj_shape = obj_data.shape
    subobj_shape = subobj_data.shape
    plt.figure(figsize=(16.0,8.0))
    plt.subplot(2, 1, 1)
    plt.imshow(obj[2].data, origin='lower',cmap='afmhot',
                   vmin=np.percentile(obj[2].data,5),
                   vmax=np.percentile(obj[2].data,90), aspect='auto')
    plt.ylabel('Position Along Slit', fontsize=14)
    plt.subplot(2, 1, 2)
    plt.imshow(subobj[2].data, origin='lower',cmap='afmhot',
                   vmin=np.percentile(subobj[2].data,5),
                   vmax=np.percentile(subobj[2].data,90), aspect='auto')
    plt.xlabel('Dispersion Axis', fontsize=14)
    plt.ylabel('Position Along Slit', fontsize=14)
    plt.tight_layout(w_pad=-0.9)
    plt.suptitle('Pre- and Post- Sky Subtraction', y=1.0)
    plt.savefig('skysub-std-{}.png'.format(obj_std_name[0]))
    plt.show()
    plt.clf()
    plt.close()

def std_extract_std():
    """ Extract standard star spectrum.
        Print position of extracted spectrum for checking. """

    print('# EXTRACTING SPECTRUM #')

    # Remove pre-existing extraction info file in the database directory.
    if os.path.exists('database/apstbcgsqgemgs{}_SCI_1_'.format(obj_std_name[0].replace('.fits',''))):
        os.remove('database/apstbcgsqgemgs{}_SCI_1_'.format(obj_std_name[0].replace('.fits','')))

    # Remove pre-existing extracted spectrum.
    if os.path.exists('estbcgsqgemgs{}'.format(obj_std_name[0])):
        os.remove('estbcgsqgemgs{}'.format(obj_std_name[0]))

    gmos.gsextract.unlearn() # Debug gsextract.
    # Task parameters.
    gsextractFlags={'fl_inter':'no', 'apwidth':'4', 'torder':'20'}
    # Extract spectrum.
    gmos.gsextract('stbcgsqgemgs{}'.format(obj_std_name[0]), **gsextractFlags) # IRAF task gsextract.

    # Row position of extracted spectrum in the standard star frame.
    center = np.genfromtxt('database/apstbcgsqgemgs{}_SCI_1_'.format(obj_std_name[0].replace('.fits','')), skip_header=5,
                        max_rows=1, usecols=2, invalid_raise=False)

    # Load standard star frame.
    obj=fits.open('stbcgsqgemgs{}'.format(obj_std_name[0]))
    obj_data = obj[2].data
    obj_shape = obj_data.shape

    # Print frame with row of extracted spectrum.
    fig = plt.figure(figsize=(14.0,6.0))
    ax1 = fig.add_subplot(111)
    plt.imshow(obj[2].data, origin='lower',cmap='afmhot',
                   vmin=np.percentile(obj[2].data,5),
                   vmax=np.percentile(obj[2].data,90), aspect='auto')
    ax1.axhline(y=center, linestyle='--', color='red',linewidth=2., alpha=0.7)
    plt.tight_layout(w_pad=-0.9)
    plt.ylabel('Position Along Slit', fontsize=14)
    plt.xlabel('Dispersion Axis', fontsize=14)
    plt.suptitle('Extracted Spectrum Position', y=1.0, fontsize=14)
    plt.savefig('extract_std-{}.png'.format(obj_std_name[0]))
    plt.show()
    plt.clf()
    plt.close()

    # Check if the spectrum position is correct.
    # Select another row to extract the spectrum.
    while True:
        print('')
        answer1 = raw_input('Are you satisfied with the extracted spectrum position? [y/n]')
        if answer1 == "y":
            break

        if answer1 == "n":
            print('')
            answer2 = raw_input('Type the new row position for extracting the spectrum: ')

            # Remove extraction info (last) file in the database directory.
            os.remove('database/aplast')
            # Remove extracted spectrum.
            os.remove('estbcgsqgemgs{}'.format(obj_std_name[0]))

            # Open extraction info file in the database directory.
            lines = open('database/apstbcgsqgemgs{}_SCI_1_'.format(obj_std_name[0].replace('.fits',''))).read().splitlines()
            lines[5] = '	center	1566. {}'.format(answer2)
            # Write new selected row to extract spectrum.
            open('database/apstbcgsqgemgs{}_SCI_1_'.format(obj_std_name[0].replace('.fits','')),'w').write('\n'.join(lines))

            gmos.gsextract.unlearn() # Debug gsextract.
            # Task parameter.
            gsextractFlags={'fl_inter':'no', 'apwidth':'4', 'torder':'20'}
            # Extract spectrum.
            gmos.gsextract('stbcgsqgemgs{}'.format(obj_std_name[0]), **gsextractFlags) # IRAF task gsextract.

            # Row position of extracted spectrum in the standard star frame.
            center = np.genfromtxt('database/apstbcgsqgemgs{}_SCI_1_'.format(obj_std_name[0].replace('.fits','')), skip_header=5,
                        max_rows=1, usecols=2, invalid_raise=False)

            # Load standard star frame.
            obj=fits.open('stbcgsqgemgs{}'.format(obj_std_name[0]))
            obj_data = obj[2].data
            obj_shape = obj_data.shape

            # Print frame with row of extracted spectrum.
            fig = plt.figure(figsize=(14.0,6.0))
            ax1 = fig.add_subplot(111)
            plt.imshow(obj[2].data, origin='lower',cmap='afmhot',
                           vmin=np.percentile(obj[2].data,5),
                           vmax=np.percentile(obj[2].data,90), aspect='auto')
            ax1.axhline(y=center, linestyle='--', color='red',linewidth=2., alpha=0.7)
            plt.tight_layout(w_pad=-0.9)
            plt.ylabel('Position Along Slit', fontsize=14)
            plt.xlabel('Dispersion Axis', fontsize=14)
            plt.suptitle('Extracted Spectrum Position', y=1.0, fontsize=14)
            plt.savefig('extract_std-{}.png'.format(obj_std_name[0]))
            plt.show()
            plt.clf()
            plt.close()

        else:
            print "Type y or n"

    # Load extracted standard star spectrum.
    obj=fits.open('estbcgsqgemgs{}'.format(obj_std_name[0]))
    obj_header = obj[2].header
    obj_data = obj[2].data
    obj_shape = obj_data.shape
    crval = obj_header['CRVAL1']
    cd1_1 = obj_header['CD1_1']

    # Print extracted standard star spectrum
    fig, ax = plt.subplots(figsize=(14.0,6.0))
    plt.plot(crval + cd1_1*np.arange(1,len(obj[2].data)+1,1), obj[2].data, linewidth=0.55)
    ax.xaxis.set_major_locator(MultipleLocator(500))
    ax.xaxis.set_minor_locator(MultipleLocator(50))
    ax.set_ylim(np.percentile(obj[2].data,5), np.percentile(obj[2].data,95))
    plt.ylabel('Counts', fontsize=14)
    plt.xlabel(r'Wavelength $\ [\AA]$', fontsize=14)
    plt.title('Extracted Spectrum', fontsize=14)
    plt.tight_layout(w_pad=-0.9)
    plt.savefig('extracted_spec_std-{}.png'.format(obj_std_name[0]))
    plt.show()
    plt.clf()
    plt.close()

def std_calib_std():
    """ Create sensitivity function for the standard star.
        Calibrate standard star spectrum.
        Plot sensitivity function and the calibrated spectrum
        of the standard star. """

    print('# CREATING CALIBRATION FILES #')

    # Remove pre-existing sensitivity function.
    if os.path.exists('sens'):
        os.remove('sens')

    # Remove pre-existing std file.
    if os.path.exists('std'):
        os.remove('std')

    # Remove pre-existing log file.
    if os.path.exists('logstandard'):
        os.remove('logstandard')

    # Load standard star file.
    obj = fits.open('estbcgsqgemgs{}'.format(obj_std_name[0]))
    obj_header = obj[0].header
    # Name of standard star.
    obj_name = obj_header['OBJECT']

    # Convert name to IRAF format.
    std_iraf_name={'L745-46A': 'l745', 'EG21': 'eg21', 'HD217086': 'hd217086',
     'EG81': 'eg81','Feige34': 'feige34', 'LTT1788': 'l1788', 'LTT3864': 'l3864',
     'G191-B2B': 'g191b2b', 'HZ43': 'hz43', 'Feige56': 'f56',
     'HD192281': 'hd192281', 'HZ44': 'hz44', 'HZ21': 'hz21',
     'LTT3218': 'l3218', 'eg131': 'eg131', 'LTT4816': 'l4816', 'LTT377': 'l377',
     'Feige110': 'feige110', 'LTT9491': 'l9491',
     'Hiltner600': 'hilt600', 'LTT1020': 'l1020',
     'LTT4364': 'l4364', 'CD-329927': 'cd32',
     'BD+75325': 'bd75325', 'LTT7987': 'l7987',
     'BD+284211': 'bd284211', 'LTT6248': 'l6248',
     'LTT9239': 'l9239', 'LTT2415': 'l2415',
     'Feige67': 'feige67', 'Feige66': 'feige66',
     'EG274': 'eg274', 'LTT7379': 'l7379'}

    std_name = std_iraf_name[str(obj_name)]

    # Dictionary of GEMINI/IRAF standard stars and their directories.
    dic_std = {'bd284211':'onedstds$spec50cal/','bd75325':'onedstds$oke90/',
        'cd32':'onedstds$ctionewcal/','eg21':'onedstds$ctionewcal/',
        'eg81':'onedstds$spec50cal/','eg131':'gmos$calib/',
        'eg274':'onedstds$ctionewcal/','feige34':'onedstds$spec50cal/',
        'f56':'onedstds$ctionewcal/', 'feige66':'onedstds$spec50cal/',
        'feige67':'onedstds$spec50cal/','feige110':'onedstds$spec50cal/',
        'g191b2b':'onedstds$spec50cal/', 'hilt600':'onedstds$spec50cal/',
        'hd192281':'onedstds$spec50cal/','hd217086':'onedstds$spec50cal/',
        'hz21':'onedstds$oke90/', 'hz43':'onedstds$iidscal/',
        'hz44':'onedstds$spec50cal/','l745':'onedstds$ctionewcal/',
        'l377':'onedstds$ctionewcal/','l1020':'onedstds$ctionewcal/',
        'l1788':'onedstds$ctionewcal/','l2415':'onedstds$ctionewcal/',
        'l3218':'onedstds$ctionewcal/','l3864':'onedstds$ctionewcal/',
        'l4364':'onedstds$ctionewcal/','l4816':'onedstds$ctionewcal/',
        'l6248':'onedstds$ctionewcal/','l7379':'onedstds$ctionewcal/',
        'l7987':'onedstds$ctionewcal/','l9239':'onedstds$ctionewcal/',
        'l9491':'onedstds$ctionewcal/',}

    func='spline3' # Function used to interpolate sensitivity function.
    ord='25' # Order of interpolating fuction.

    gmos.gsstandard.unlearn() # Debug gsstandard.
    # Task parameters.
    gsstandardFlags={'sfile':'std','sfunction':'sens',
                    'starname':str(std_name),'logfile':'logstandard',
                    'caldir':str(dic_std[str(std_name)]),
                    'fl_inter':'no', 'function':func, 'order':ord}
    # Create sensitivity function.
    gmos.gsstandard('estbcgsqgemgs{}'.format(obj_std_name[0]), **gsstandardFlags) # IRAF task gsstandard.

    # Load sensitivity function.
    sens = fits.open('sens.fits')
    sens_data = sens[0].data
    sens_header = sens[0].header
    crval1 = sens[0].header['CRVAL1']
    cd1_1 = sens[0].header['CD1_1']
    wavelength_sens = crval1 + cd1_1*(np.arange(1,len(sens_data)+1,1))

    # Read 'logstandard' file.
    # Number of lines for the needed information.
    number_of_lines = np.genfromtxt('logstandard', skip_header=42, usecols=2,
                                    max_rows=1, invalid_raise=False)
    # RMS of function interpolation.
    RMS_logstandard = np.genfromtxt('logstandard', skip_header=42, usecols=4,
                                    max_rows = 1, invalid_raise=False)
    # Wavelength for each point.
    wavelength_logstandard = np.genfromtxt('logstandard', skip_header=45, usecols=0,
                                    max_rows = number_of_lines, invalid_raise=False)
    # Fitted points.
    fit_logstandard = np.genfromtxt('logstandard', skip_header=45, usecols=1,
                                    max_rows = number_of_lines, invalid_raise=False)
    # Residual points.
    resid_logstandard = np.genfromtxt('logstandard', skip_header=45, usecols=3,
                                    max_rows = number_of_lines, invalid_raise=False)

    # Plot sensitivity function, its order, RMS and residual.
    plt.figure(figsize=(14.0,6.0))
    ax1 = plt.subplot(2,1,1)
    ax1.plot(wavelength_sens, sens_data)
    ax1.scatter(wavelength_logstandard, fit_logstandard, color='red', s=25, marker='x')
    ax1.set_ylabel('Sensitivity', fontsize=12)
    ax1.set_xlabel('Wavelength', fontsize=12)
    ax2 = plt.subplot(2,1,2)
    ax2.scatter(wavelength_logstandard, resid_logstandard, s=25, color='red', marker='x')
    ax2.axhline(y=0, linestyle='--')
    ax2.set_xlabel('Wavelength', fontsize=12)
    ax2.set_ylabel('Residual', fontsize=12)
    plt.tight_layout(w_pad=-0.9)
    plt.suptitle('Function = {}  Order = {} RMS = {}'.format(func, ord, RMS_logstandard), fontsize=12,y=1.0)
    plt.savefig('plot-gsstandard-{}.png'.format(obj_std_name[0]))
    plt.show()

    print('# CALIBRATING... # ')

    # Remove pre-existing calibrated spectrum.
    if os.path.exists('cestbcgsqgemgs{}'.format(obj_std_name[0])):
        os.remove('cestbcgsqgemgs{}'.format(obj_std_name[0]))

    gmos.gscalibrate.unlearn() # Debug gscalibrate.
    # Calibrate standard star spectrum.
    gmos.gscalibrate('estbcgsqgemgs{}'.format(obj_std_name[0])) # IRAF task gscalibrate.

    # Load calibrated spectrum.
    obj=fits.open('cestbcgsqgemgs{}'.format(obj_std_name[0]))
    obj_header = obj[2].header
    obj_data = obj[2].data
    obj_shape = obj_data.shape
    crval = obj_header['CRVAL1']
    cd1_1 = obj_header['CD1_1']

    # Plot calibrated spectrum of standard star.
    fig, ax = plt.subplots(figsize=(14.0,6.0))
    plt.plot(crval + cd1_1*np.arange(1,obj_shape[0]+1,1), obj[2].data,linewidth=0.55)
    ax.xaxis.set_major_locator(MultipleLocator(500))
    ax.xaxis.set_minor_locator(MultipleLocator(50))
    ax.set_ylim(np.percentile(obj[2].data,5), np.percentile(obj[2].data,95))
    plt.ylabel('Flux [ergs cm$^{-2}$ s$^{-1}$ $\ \AA$$^{-1}$] ', fontsize=14)
    plt.xlabel(r'Wavelength $\ [\AA]$', fontsize=14)
    plt.title('Calibrated Spectrum', fontsize=14)
    plt.tight_layout(w_pad=-0.9)
    plt.savefig('calib-spec-std-{}.png'.format(obj_std_name[0]))
    plt.show()
    plt.clf()
    plt.close()

# Reduction and calibration of SCIENCE OBJECT files.
print "------------------------------"
print "# REDUCTION OF SCIENCE OBJECT #"
print "------------------------------"

def obj_gbias():
    """ Apply overscan correction and trim individual bias frames.
        Create Master Bias. Plot Master Bias and pixel counting. """

    print('# CREATING MASTER BIAS #')

    # Remove pre-existing Master Bias.
    if os.path.exists('Bias.fits'):
        os.remove('Bias.fits')

    gmos.gbias.unlearn() # Debug gbias.
    # Set the task parameters.
    biasFlags = {'rawpath':'raw', 'fl_over':'yes',
                'fl_trim':'yes', 'fl_vardq':'yes'}
    # Create Master Bias.
    gmos.gbias('@bias_obj.txt', 'Bias.fits', **biasFlags) # IRAF task gbias.

    # Load Master Bias.
    obj=fits.open('Bias.fits')
    obj_data = obj[2].data
    obj_shape = obj_data.shape

    # Print Master Bias.
    plt.figure(figsize=(14.0,4.0))
    for i in range(len(np.arange(0,12,1))):
        ax = plt.subplot(1, 12,i+1)
        plt.imshow(obj[i+1].data, origin='lower',cmap='afmhot',
                   vmin=np.percentile(obj[i+1].data,5),
                   vmax=np.percentile(obj[i+1].data,90), aspect='auto')
        if i == 0:
            ax.yaxis.set_visible(True)
            ax.set_ylabel('Position Along Slit', fontsize=14)
        else:
            ax.yaxis.set_visible(False)

    plt.tight_layout(w_pad=-0.9)
    plt.suptitle('Master BIAS', y=1.0, fontsize=14)
    plt.savefig('master-bias-obj-{}.png'.format(obj_sci_name[0]))
    plt.show()
    plt.clf()
    plt.close()

    # Print the pixel counting through a line cut.
    plt.figure(figsize=(16.0,8.0))
    for j in range(len(np.arange(0,12,1))):
        ax1 = plt.subplot(3, 12,j+1)
        ax1.set_ylim(min(obj[1].data[int(0.3*obj_shape[0]),1:obj_shape[1]]),
                        max(obj[1].data[int(0.3*obj_shape[0]),1:obj_shape[1]]))
        ax1.plot(np.arange(1,obj_shape[1],1),
                    obj[j+1].data[int(0.3*obj_shape[0]),1:obj_shape[1]],linewidth=0.5)

        ax2 = plt.subplot(3, 12,12+j+1)
        ax2.set_ylim(min(obj[1].data[int(0.5*obj_shape[0]),1:obj_shape[1]]),
                        max(obj[1].data[int(0.5*obj_shape[0]),1:obj_shape[1]]))
        ax2.plot(np.arange(1,obj_shape[1],1),
                    obj[j+1].data[int(0.5*obj_shape[0]),1:obj_shape[1]],linewidth=0.5)

        ax3 = plt.subplot(3, 12, 24+j+1)
        ax3.set_ylim(min(obj[1].data[int(0.7*obj_shape[0]),1:obj_shape[1]]),
                        max(obj[1].data[int(0.7*obj_shape[0]),1:obj_shape[1]]))
        ax3.plot(np.arange(1,obj_shape[1],1),
                    obj[j+1].data[int(0.7*obj_shape[0]),1:obj_shape[1]],linewidth=0.5)
        if j == 0:
            ax1.yaxis.set_visible(True)
            ax1.set_ylabel('Counts [row={}]'.format(int(0.3*obj_shape[0])), fontsize=14)
            ax2.yaxis.set_visible(True)
            ax2.set_ylabel('Counts [row={}]'.format(int(0.5*obj_shape[0])), fontsize=14)
            ax3.yaxis.set_visible(True)
            ax3.set_ylabel('Counts [row={}]'.format(int(0.7*obj_shape[0])), fontsize=14)
        else:
            ax1.yaxis.set_visible(False)
            ax2.yaxis.set_visible(False)
            ax3.yaxis.set_visible(False)

    plt.tight_layout(w_pad=-0.9)
    plt.suptitle('Pixel Counting',y=1.0, fontsize=14)
    plt.savefig('pixel-counting-bias-obj-{}.png'.format(obj_sci_name[0]))
    plt.show()
    plt.close()

def obj_reduc_arc():
    """ Apply overscan correction and mosaic arc frames. """

    print('# REDUCING ARC LAMP #')

    # Remove pre-existing calibrated files.
    if os.path.exists('gs{}'.format(arc_sci_name[0])):
        os.remove('gs{}'.format(arc_sci_name[0]))

    gmos.gsreduce.unlearn() # Debug gsreduce.
    # Set the task parameters.
    gsreduceFlags1={'rawpath':'raw', 'fl_bias':'yes',
                    'fl_flat':'no', 'fl_over':'yes',
                    'bias':'Bias', 'fl_gmos':'yes'}
    # Reduce arc frames.
    gmos.gsreduce(str(arc_sci_name[0]), **gsreduceFlags1) # IRAF task gsreduce.

def obj_wavelength_arc():
    """ Create a wavelength solution based on arc frames.
        Print the difference of the calculated and correct wavelength values
        for the estimated lines."""

    print('# CALIBRATING WAVELENGTH #')

    # Remove pre-existing wavelength solution files on database directory.
    if os.path.exists('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits',''))):
        os.remove('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')))

    # Load reduced arc frame.
    obj=fits.open('gs{}'.format(arc_sci_name[0]))
    obj_data = obj[2].data
    arc_shape = obj_data.shape

    gmos.gswavelength.unlearn() # Debug gswavelength.
    # Set the task parameters.
    gswavelengthFlags={'nsum':str(arc_shape[0]/3), 'step':str(arc_shape[0]/3),
                        'fwidth':'7', 'gsigma':'1.5','cradius':'12',
                        'minsep':'7', 'order':'6', 'fl_inter':'no'}
    gmos.gswavelength('gs{}'.format(arc_sci_name[0]), **gswavelengthFlags) # IRAF task gswavelength.

    # Read wavelength solution file on database directory.
    # Autoidentify.
    # Number of calculated features.
    number_of_features_auto = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')),
                                            skip_header=6, usecols=1, max_rows=1, invalid_raise=False)
    # Number of calculated coefficients.
    number_of_coefficients_auto = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')),
                                            skip_header=7+int(number_of_features_auto)+8, usecols=1,
                                                max_rows=1, invalid_raise=False)
    # gswavelength flags to discard outlier values.
    wave_flag_auto = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')), skip_header=7,
                                usecols=5, max_rows=int(number_of_features_auto), invalid_raise=False)
    # Row number.
    wave_auto_col_0 = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')), skip_header=7,
                                usecols=0, max_rows=int(number_of_features_auto), invalid_raise=False)
    # Corrected line wavelength.
    wave_auto_col_1  = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')), skip_header=7,
                                usecols=1, max_rows=int(number_of_features_auto), invalid_raise=False)
    # Calculated line wavelength.
    wave_auto_col_2  = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')), skip_header=7,
                                usecols=2, max_rows=int(number_of_features_auto), invalid_raise=False)

    # Reidentify.
    # Number of calculated features.
    number_of_features_re1 = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')),
                             skip_header=7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)+7,
                                        usecols=1, max_rows=1, invalid_raise=False)

    number_of_coefficients_re1 = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')),
           skip_header=7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)+8+int(number_of_features_re1)+8,
                                        usecols=1, max_rows=1, invalid_raise=False)

    # gswavelength flags to discard outlier values.
    wave_flag_re1 = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')),
                                skip_header=7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)+8,
                                usecols=5, max_rows=int(number_of_features_re1), invalid_raise=False)
    # Row number.
    wave_re1_col_0 = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')),
                                skip_header=7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)+8, usecols=0,
                                max_rows=int(number_of_features_re1), invalid_raise=False)
    # Corrected line wavelength.
    wave_re1_col_1 = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')),
                                skip_header=7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)+8, usecols=1,
                                max_rows=int(number_of_features_re1), invalid_raise=False)
    # Calculated line wavelength.
    wave_re1_col_2 = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')),
                                skip_header=7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)+8, usecols=2,
                                max_rows=int(number_of_features_re1), invalid_raise=False)

    # Reidentify.
    # Number of calculated features.

    number_of_features_re2 = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')),
                                        skip_header=(7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)
                                        +8+int(number_of_features_re1)+9+int(number_of_coefficients_re1)+7),
                                           usecols=1, max_rows=1, invalid_raise=False)

    # gswavelength flags to discard outlier values.
    wave_flag_re2 = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')),
                                skip_header=(7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)
                                        +8+int(number_of_features_re1)+9+int(number_of_coefficients_re1)+8),
                                  usecols=5, max_rows=int(number_of_features_re2), invalid_raise=False)
    # Row number.
    wave_re2_col_0 = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')),
                                skip_header=(7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)
                                        +8+int(number_of_features_re1)+9+int(number_of_coefficients_re1)+8),
                                  usecols=0, max_rows=int(number_of_features_re2), invalid_raise=False)
    # Corrected line wavelength.
    wave_re2_col_1 = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')),
                                skip_header=(7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)
                                        +8+int(number_of_features_re1)+9+int(number_of_coefficients_re1)+8),
                                  usecols=1, max_rows=int(number_of_features_re2), invalid_raise=False)
    # Calculated line wavelength.
    wave_re2_col_2 = np.genfromtxt('database/idgs{}_001'.format(arc_sci_name[0].replace('.fits','')),
                                skip_header=(7+int(number_of_features_auto)+9+int(number_of_coefficients_auto)
                                        +8+int(number_of_features_re1)+9+int(number_of_coefficients_re1)+8),
                                  usecols=2, max_rows=int(number_of_features_re2), invalid_raise=False)

    # gswavelength flags
    flag_auto = np.where(wave_flag_auto[0:,] == 1) # Autoidentify.
    flag_re1 = np.where(wave_flag_re1[0:,] == 1) # Reidentify.
    flag_re2 = np.where(wave_flag_re2[0:,] == 1) # Reidentify.

    # RMS estimate.

    # Autoidentify.
    rows_auto = wave_auto_col_0[0:,][flag_auto]
    delta_lambda_auto = wave_auto_col_2[0:,][flag_auto] - wave_auto_col_1[0:,][flag_auto]
    rms_auto = np.sqrt(np.sum(delta_lambda_auto**2) / len(rows_auto))

    print("[AUTOIDENTIFY] RMS = ", rms_auto)

    hig_than_rms_auto=[] # Values higher than RMS.
    for l in range(len(delta_lambda_auto)):
        if np.abs(delta_lambda_auto[l]) > rms_auto:
            hig_than_rms_auto.append( wave_auto_col_2[0:,][flag_auto][l])
    # Print number of lines with values diverging from the correct value
    # whith a difference higher thant the RMS.
    print("[AUTOIDENTIFY] There are {} identified lines diverging from the"
            " observed value with differences higher than the RMS :".format(len(hig_than_rms_auto)), hig_than_rms_auto)

     # Reidentify.
    rows_re1 = wave_re1_col_0[0:,][flag_re1]
    delta_lambda_re1 = wave_re1_col_2[0:,][flag_re1] - wave_re1_col_1[0:,][flag_re1]
    rms_re1 = np.sqrt(np.sum(delta_lambda_re1**2) / len(rows_re1))

    print('[REIDENTIFY] RMS = ', rms_re1)

    hig_than_rms_re1=[] # Values higher than RMS.
    for l in range(len(delta_lambda_re1)):
        if np.abs(delta_lambda_re1[l]) > rms_re1:
            hig_than_rms_re1.append(wave_re1_col_2[0:,][flag_re1][l])
    # Print number of lines with values diverging from the correct value
    # whith a difference higher thant the RMS.
    print("[REIDENTIFY] There are {} identified lines diverging from the"
            " observed value with differences higher than the RMS :".format(len(hig_than_rms_re1)), hig_than_rms_re1)

    # Reidentify.
    rows_re2 = wave_re2_col_0[0:,][flag_re2]
    delta_lambda_re2 = wave_re2_col_2[0:,][flag_re2] - wave_re2_col_1[0:,][flag_re2]
    rms_re2 = np.sqrt(np.sum(delta_lambda_re2**2) / len(rows_re2))

    print('[REIDENTIFY] RMS = ', rms_re2)

    hig_than_rms_re2=[]  # Values higher than RMS.
    for l in range(len(delta_lambda_re2)):
        if np.abs(delta_lambda_re2[l]) > rms_re2:
            hig_than_rms_re2.append(wave_re2_col_2[0:,][flag_re2][l])
    # Print number of lines with values diverging from the correct value
    # whith a difference higher thant the RMS.
    print("[REIDENTIFY] There are {} identified lines diverging from the"
            " observed value with differences higher than the RMS :".format(len(hig_than_rms_re2)), hig_than_rms_re2)

    # Print the difference of the calculated and correct wavelength values
    # for the estimated lines.
    # Autoidentify.
    fig = plt.figure(figsize=(14.0,6.0))
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twiny()
    ax3 = ax1.twiny()
    ax4 = ax1.twiny()
    ax1.scatter(rows_auto,np.abs(delta_lambda_auto), color='white' )
    ax2.scatter(wave_auto_col_2[0:,][flag_auto], np.abs(delta_lambda_auto), color='coral')
    ax2.invert_xaxis()
    plt.title('Autoidentify', y=1.10, fontsize=14)
    ax2.set_xlabel(r'$\lambda_{identified} \ [\AA]$', fontsize=14)
    ax1.set_xlabel('Pixel position', fontsize=14)
    ax1.set_ylabel(r'|$\lambda_{identified} - \lambda_{fitted}| \ [\AA]$', fontsize=14)
    ax3.axhline(y=0.2, linestyle='--')
    ax3.xaxis.set_visible(False)
    ax4.axhline(y=rms_auto, linestyle=':', label='RMS = {}'.format(rms_auto))
    ax4.xaxis.set_visible(False)
    plt.tight_layout(w_pad=-0.9)
    ax4.legend()
    plt.savefig('autoidentify_obj-{}.png'.format(obj_sci_name[0]))
    plt.show()
    plt.close()

    # Reidentify.
    fig = plt.figure(figsize=(14.0,6.0))
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twiny()
    ax3 = ax1.twiny()
    ax4 = ax1.twiny()
    ax1.scatter(rows_re1,np.abs(delta_lambda_re1), color='white' )
    ax2.scatter(wave_re1_col_2[0:,][flag_re1] ,np.abs(delta_lambda_re1), color='coral')
    ax2.invert_xaxis()
    plt.title('Reidentify', y=1.10, fontsize=14)
    ax2.set_xlabel(r'$\lambda_{identified} \ [\AA]$', fontsize=14)
    ax1.set_xlabel('Pixel position', fontsize=14)
    ax1.set_ylabel(r'|$\lambda_{identified} - \lambda_{fitted}| \ [\AA]$', fontsize=14)
    ax3.axhline(y=0.2, linestyle='--')
    ax3.xaxis.set_visible(False)
    ax4.axhline(y=rms_re1, linestyle=':', label='RMS = {}'.format(rms_re1))
    ax4.xaxis.set_visible(False)
    plt.tight_layout(w_pad=-0.9)
    ax4.legend()
    plt.show()
    plt.close()

    # Reidentify.
    fig = plt.figure(figsize=(14.0,6.0))
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twiny()
    ax3 = ax1.twiny()
    ax4 = ax1.twiny()
    ax1.scatter(rows_re2,np.abs(delta_lambda_re2), color='white' )
    ax2.scatter(wave_re2_col_2[0:,][flag_re2] ,np.abs(delta_lambda_re2), color='coral')
    ax2.invert_xaxis()
    plt.title('Reidentify', y=1.10, fontsize=14)
    ax2.set_xlabel(r'$\lambda_{identified} \ [\AA]$', fontsize=14)
    ax1.set_xlabel('Pixel position', fontsize=14)
    ax1.set_ylabel(r'|$\lambda_{identified} - \lambda_{fitted}| \ [\AA]$', fontsize=14)
    ax3.axhline(y=0.2, linestyle='--')
    ax3.xaxis.set_visible(False)
    ax4.axhline(y=rms_re2, linestyle=':', label='RMS = {}'.format(rms_re2))
    ax4.xaxis.set_visible(False)
    plt.tight_layout(w_pad=-0.9)
    ax4.legend()
    plt.show()
    plt.close()


def obj_transf_arc():
    """ Transform arc files. """

    print('# TRANSFORMING ARC #')

    # Remove pre-existing transformed files.
    if os.path.exists('tgs{}'.format(arc_sci_name[0])):
        os.remove('tgs{}'.format(arc_sci_name[0]))

    gmos.gstransform.unlearn() # Debug gstransform.
    # Set the task parameters.
    gstransformFlags={'wavtranam':'gs{}'.format(arc_sci_name[0])}
    # Transform arc files.
    gmos.gstransform('gs{}'.format(arc_sci_name[0]), **gstransformFlags) # IRAF task gstransform.

def obj_reduc_flat():
    """ Subtract bias from individual flat frames. """

    print('# REDUCING RAW FLATS #')

    # Open individual flat frames.
    f = open('flat_obj.txt', 'r')
    for flatfile in f:
        # Remove pre-existing processed files.
        if os.path.exists('gs{}'.format(flatfile.replace('\n',''))):
            os.remove('gs{}'.format(flatfile.replace('\n','')))

        gmos.gsreduce.unlearn() # Debug gsreduce.
        # Set the task parameters.
        gsreduceFlags={'rawpath':'raw', 'fl_bias':'yes',
                        'fl_flat':'no', 'fl_fixpix':'no',
                        'bias':'Bias.fits','fl_gmos':'no',
                        'fl_gsappwave':'no', 'fl_cut':'no'}
        # Reduce flat files.
        gmos.gsreduce(str(flatfile.replace('\n','')), **gsreduceFlags) # IRAF task gsreduce.
    f.close()

def obj_qecorr_flat():
    """ Apply quantum efficiency correction to individual
        flat frames. """

    print('# QUANTUM-CORRECTING FLAT #')

    # Open individual flat frames.
    f = open('flat_obj.txt', 'r')
    for flatfile in f:
        # Remove pre-existing processed files.
        if os.path.exists('qgs{}'.format(flatfile.replace('\n',''))):
            os.remove('qgs{}'.format(flatfile.replace('\n','')))

        gmos.gqecorr.unlearn() # Debug gqecorr.
        # Set the task parameters.
        qecorrFlags= {'refimage':'gs{}'.format(arc_sci_name[0]),
                    'fl_keep':'yes'}
        # Apply quantum efficiency correction.
        gmos.gqecorr('gs{}'.format(flatfile.replace('\n','')), **qecorrFlags) # IRAF task gqecorr.
    f.close()

def obj_gmosaic_flat():
    """ Mosaic individual flat frames. """

    print('# MOSAIC FLAT#')

    # Remove pre-existing list.
    if os.path.exists("mqgsflat_obj.txt"):
        os.remove("mqgsflat_obj.txt")

    # Open individual flat frames.
    f = open('flat_obj.txt', 'r')
    for flatfile in f:
        # Remove pre-existing processed files.
        if os.path.exists('mqgs{}'.format(flatfile.replace('\n',''))):
            os.remove('mqgs{}'.format(flatfile.replace('\n','')))

        gmos.gmosaic.unlearn() # Debug gmosaic.
        # Set the task parameters.
        gmosaicFlags= {'fl_fixpix':'yes'}
        # Mosaic flat frames.
        gmos.gmosaic('qgs{}'.format(flatfile.replace('\n','')), **gmosaicFlags) # IRAF task gmosaic.

        # Write name of processed files on list.
        mqgsflat = open("mqgsflat_obj.txt","a")
        mqgsflat.write('mqgs{}'.format(flatfile.replace('\n','')))
        mqgsflat.write("\n")
        mqgsflat.close()

    f.close()

def obj_masterflat():
    """ Trim individual flat frames and create Master Flat.
        Print Master Flat and pixel counting. """

    print('# CREATING MASTER FLAT #')

    # Remove pre-existing Master Flat.
    if os.path.exists('qFlat.fits'):
        os.remove('qFlat.fits')

    gmos.gsflat.unlearn() # Debug gsflat.
    # Set the task parameters.
    flatFlags = {'fl_bias':'no', 'order':'29',
                'fl_over':'no', 'fl_trim':'no',
                'fl_usegrad':'yes'}
    # Create Master Flat.
    gmos.gsflat('@mqgsflat_obj.txt', 'qFlat.fits', **flatFlags) # IRAF task gsflat.

    # Load Master Flat.
    obj=fits.open('qFlat.fits')
    obj_data = obj[2].data
    obj_shape = obj_data.shape

    # Plot Master Flat.
    plt.figure(figsize=(12.0,4.0))
    plt.imshow(obj[2].data, origin='lower',cmap='afmhot',
               vmin=np.percentile(obj[2].data,5),
               vmax=np.percentile(obj[2].data,90), aspect='auto')
    plt.ylabel('Position Along Slit', fontsize=14)
    plt.xlabel('Dispersion Axis', fontsize=14)
    plt.tight_layout(w_pad=-0.9)
    plt.suptitle('Master FLAT', y=1.0, fontsize=14)
    plt.savefig('master-flat-obj-{}.png'.format(obj_sci_name[0]))
    plt.show()
    plt.clf()
    plt.close()

    # Print the pixel counting through a line cut.
    plt.figure(figsize=(16.0,8.0))
    ax1 = plt.subplot(3, 1, 1)
    ax1.set_ylim(min(obj[2].data[int(0.3*obj_shape[0]),1:obj_shape[1]]),
                    max(obj[2].data[int(0.3*obj_shape[0]),1:obj_shape[1]]))
    ax1.set_ylabel('Counts [row={}]'.format(int(0.3*obj_shape[0])), fontsize=14)
    ax1.plot(np.arange(1,obj_shape[1],1),
                obj[2].data[int(0.3*obj_shape[0]),1:obj_shape[1]],linewidth=0.5)

    ax2 = plt.subplot(3, 1, 2)
    ax2.set_ylim(min(obj[2].data[int(0.5*obj_shape[0]),1:obj_shape[1]]),
                    max(obj[2].data[int(0.5*obj_shape[0]),1:obj_shape[1]]))
    ax2.set_ylabel('Counts [row={}]'.format(int(0.5*obj_shape[0])), fontsize=14)
    ax2.plot(np.arange(1,obj_shape[1],1),
                obj[2].data[int(0.5*obj_shape[0]),1:obj_shape[1]],linewidth=0.5)

    ax3 = plt.subplot(3, 1, 3)
    ax3.set_ylim(min(obj[2].data[int(0.7*obj_shape[0]),1:obj_shape[1]]),
                    max(obj[2].data[int(0.7*obj_shape[0]),1:obj_shape[1]]))
    ax3.set_ylabel('Counts [row={}]'.format(int(0.7*obj_shape[0])), fontsize=14)
    ax3.plot(np.arange(1,obj_shape[1],1),
                obj[2].data[int(0.7*obj_shape[0]),1:obj_shape[1]],linewidth=0.5)
    ax3.set_xlabel('Dispersion Axis', fontsize=14)

    plt.tight_layout(w_pad=-0.9)
    plt.suptitle('Pixel Counting',y=1.0, fontsize=14)
    plt.savefig('pixel-counting-flat-{}.png'.format(obj_sci_name[0]))
    plt.show()
    plt.close()

def obj_reduc1_obj():
    """ Subtract bias, apply overscan and cosmic ray correction
        to science object frames. """

    print('# 1st REDUCTION #')

    # Remove pre-existing processed files.
    if os.path.exists('gs{}'.format(obj_sci_name[0])):
        os.remove('gs{}'.format(obj_sci_name[0]))

    gmos.gsreduce.unlearn() # Debug gsreduce.
    # Task parameters.
    gsreduceFlags={'rawpath':'raw','fl_gmos':'no', 'fl_fixpix':'no',
                    'fl_flat':'no', 'fl_vardq':'yes',
                    'fl_fulldq':'yes', 'fl_bias':'yes',
                    'bias':'Bias', 'fl_inter':'no',
                    'fl_cut':'no', 'fl_gsappwave':'no',
                    'fl_over':'yes', 'fl_crspec':'yes'}
    # Reduce science object files.
    gmos.gsreduce(str(obj_sci_name[0]), **gsreduceFlags) # IRAF task gsreduce.

def obj_gemfix_obj():
    """ Improve cosmic ray and bad pixel correction.
        Print raw and corrected files for comparison. """

    print('# GEMFIX #')

    # Remove pre-existing processed files.
    if os.path.exists('gemgs{}'.format(obj_sci_name[0])):
        os.remove('gemgs{}'.format(obj_sci_name[0]))
    if os.path.exists('copy_gemgs{}'.format(obj_sci_name[0])):
        os.remove('copy_gemgs{}'.format(obj_sci_name[0]))

    gemini.gemfix.unlearn() # Debug gemfix.
    # Task parameters.
    gemfixFlags={'outimages':'gemgs{}'.format(obj_sci_name[0]),
                    'method':'fixpix', 'bitmask':'8'}
    # Fix bad pixels.
    gemini.gemfix('gs{}'.format(obj_sci_name[0]), **gemfixFlags) # IRAF task gemfix.

    # Load raw files.
    obj=fits.open('raw/{}'.format(obj_sci_name[0]))
    obj_data = obj[2].data
    obj_shape = obj_data.shape

    # Load processed files.
    gemobj=fits.open('gemgs{}'.format(obj_sci_name[0]))
    gemobj_data = gemobj[len(gemobj)-1].data
    gemobj_shape = gemobj_data.shape

    # Create copy of processed file.
    copy_gemobj = fits.HDUList([gemobj[0]])
    for n in np.arange(2,37,3):
        copy_gemobj.append(gemobj[n])
    copy_gemobj.writeto('copy_gemgs{}'.format(obj_sci_name[0]))
    new_gemobj = fits.open('copy_gemgs{}'.format(obj_sci_name[0]))
    gemobj_data = gemobj[len(gemobj)-1].data
    gemobj_shape = gemobj_data.shape

    # Print raw and corrected files.
    plt.figure(figsize=(16.0,8.0))
    for i in range(len(np.arange(0,12,1))):
        ax1 = plt.subplot(2,12,i+1)
        ax1.imshow(obj[i+1].data, origin='lower',cmap='afmhot',
                   vmin=np.percentile(obj[i+1].data,5),
                   vmax=np.percentile(obj[i+1].data,90), aspect='auto')
        ax2 = plt.subplot(2,12,12+i+1)
        ax2.imshow(new_gemobj[i+1].data, origin='lower',cmap='afmhot',
                   vmin=np.percentile(new_gemobj[i+1].data,5),
                   vmax=np.percentile(new_gemobj[i+1].data,90), aspect='auto')
        if i == 0:
            ax1.yaxis.set_visible(True)
            ax1.set_ylabel('Position Along Slit', fontsize=14)
            ax2.yaxis.set_visible(True)
            ax2.set_ylabel('Position Along Slit', fontsize=14)
        else:
            ax1.yaxis.set_visible(False)
            ax2.yaxis.set_visible(False)
    plt.tight_layout(w_pad=-0.9)
    plt.suptitle('Pre- and Post- Cosmic Ray Rejection', y=1.0, fontsize=14)
    plt.savefig('gemfix_obj_{}.png'.format(obj_sci_name[0]))
    plt.show()
    plt.clf()
    plt.close()


def obj_qecorr_obj():
    """ Apply quantum efficiency correction to science object frames. """

    print('# QUANTUM-CORRECTING #')

    # Remove pre-existing processed files.
    if os.path.exists('qgemgs{}'.format(obj_sci_name[0])):
        os.remove('qgemgs{}'.format(obj_sci_name[0]))

    # Open list of individual flat frames.
    flatfile_list=[]
    f = open('flat_obj.txt', 'r')
    for flatfile in f:
        flatfile_list.append(flatfile)
    f.close()

    gmos.gqecorr.unlearn() # Debug gqecorr.
    # Task parameters
    qecorrFlags= {'refimage':'gs{}'.format(arc_sci_name[0]),
                    'corrima':'qgs{}'.format(flatfile_list[0].replace('\n',''))}
    # Apply quantum efficiency correction.
    gmos.gqecorr('gemgs{}'.format(obj_sci_name[0]), **qecorrFlags) # IRAF task gqecorr.

def obj_reduc2_obj():
    """ Apply flat field correction to science object frames. """

    print '# 2nd REDUCTION #'

    # Remove pre-existing processed files.
    if os.path.exists('gsqgemgs{}'.format(obj_sci_name[0])):
        os.remove('gsqgemgs{}'.format(obj_sci_name[0]))

    gmos.gsreduce.unlearn() # Debug gsreduce.
    # Task parameters.
    gsreduceFlags={'fl_bias':'no', 'fl_flat':'yes',
                    'fl_over':'no', 'flat':'qFlat',
                    'fl_trim':'no'}
    # Apply flat correction.
    gmos.gsreduce('qgemgs{}'.format(obj_sci_name[0]), **gsreduceFlags) # IRAF task gsreduce.

def obj_badcolumn_obj():
    """ Print science object frame for bad column checking.
        Interpolate bad columns. """

    print('# BAD COLUMN CHECKING #')

    # Remove pre-existing processed files.
    if os.path.exists('bcgsqgemgs{}'.format(obj_sci_name[0])):
        os.remove('bcgsqgemgs{}'.format(obj_sci_name[0]))
    # Create copy of science object file to apply bad column correction.
    iraf.copy('gsqgemgs{}'.format(obj_sci_name[0]), 'bcgsqgemgs{}'.format(obj_sci_name[0]))
    # Load copy.
    obj=fits.open('bcgsqgemgs{}'.format(obj_sci_name[0]))

    # Check if a bad column mask is already available in the directory.
    if os.path.exists("maskbadcol.txt"):
        while True:
            try:
                print('')
                answer = raw_input("The file 'maskbadcol.txt' is available in this directory. "
                                    " Do you wish to apply this mask to your spectrum? (y/n) ")
                if answer=='y':
                    # Remove pre-existing mask.
                    if os.path.exists("maskbadcol.pl"):
                        os.remove("maskbadcol.pl")

                    # Create mask based on coordinates text file.
                    iraf.text2mask('maskbadcol.txt', 'maskbadcol.pl',
                                    obj[2].shape[1], obj[2].shape[0]) # IRAF task 'text2mask'.

                    # Interpolate bad columns using mask.
                    iraf.fixpix('bcgsqgemgs{}[2]'.format(obj_sci_name[0]),
                                    'maskbadcol.pl', linterp='1,2,3,4') # IRAF task 'fixpix'.
                    break

                if answer=='n':
                    break

                else:
                    print('Please, type y or n ')

            except(NameError, SyntaxError,IndexError):
                    print('')
                    print("Check if you typed a correct line number. ")

    # Select a line in the science object frame and print the pixel counting
    # through the line for bad column checking.
    while True:
        try:
            print('')
            # Selected line.
            line = int(input('Choose a line for bad column checking: ' ))
            print('')

            xaxis=np.arange(1, obj[2].data.shape[1],1)
            yaxis=obj[2].data[line,1:obj[2].data.shape[1]]

            # Print science object frame and pixel counting
            # through the selected line.
            plt.figure(figsize=(16.0,8.0))
            plt.figure(figsize=(16.0,8.0))
            ax1=plt.subplot(211)
            ax1.imshow(obj[2].data, origin='lower',cmap='afmhot',
                           vmin=np.percentile(obj[2].data,1),
                           vmax=np.percentile(obj[2].data,99), aspect='auto')
            ax1.axhline(y=line, linestyle='--', color='red',linewidth=2., alpha=0.7)
            ax1.set_ylabel('Position Along Slit', fontsize=14)
            ax2=plt.subplot(212)
            ax2.plot(xaxis, yaxis, color='red' )
            ax2.set_xlim(left=np.min(xaxis), right=np.max(xaxis))
            ax2.set_ylabel('Counts', fontsize=14)
            ax2.set_xlabel('Dispersion Axis', fontsize=14)
            plt.show()

            answer = raw_input('Do you wish to select another line? (y/n) ')

            if answer=='n':
                break
            if answer=='y':
                print('')
            else:
                print('Please, type y or n ')

        except(NameError, SyntaxError,IndexError):
                print('')
                print("Check if you typed a correct line number. ")

    # Select the inital and final position along the x-axis of
    # the columns to interpolate.
    # Create a mask and interpolate bad column.
    while True:
        try:
            print('')
            answer2 = raw_input('Do you wish to interpolate a bad column? (y/n) ')
            print('')

            if answer2=='n':
                break
            if answer2=='y':

                while True:
                    try:
                        print('')
                        # Inital x position of the bad column.
                        x1 = int(input('Select a column to interpolate (x min): ' ))
                        print('')
                        # Final x position of the bad column.
                        x2 = int(input('Select a column to interpolate (x max): ' ))

                        # Create text file with the column coordinates.
                        bias_obj_txt = open("maskbadcol.txt","a")
                        bias_obj_txt.write('{} {} 1 {}'.format(x1, x2, obj[2].shape[0]))
                        bias_obj_txt.write("\n")
                        bias_obj_txt.close()

                        # Remove pre-existing mask.
                        if os.path.exists("maskbadcol.pl"):
                            os.remove("maskbadcol.pl")

                        # Create mask based on coordinates text file.
                        iraf.text2mask('maskbadcol.txt', 'maskbadcol.pl',
                                        obj[2].shape[1], obj[2].shape[0]) # IRAF task 'text2mask'.

                        # Interpolate bad columns using mask.
                        iraf.fixpix('bcgsqgemgs{}[2]'.format(obj_sci_name[0]),
                                        'maskbadcol.pl', linterp='1,2,3,4') # IRAF task 'fixpix'.

                        # Print corrected science object frame and pixel counting
                        # through the selected line.
                        obj2=fits.open('bcgsqgemgs{}'.format(obj_sci_name[0]))
                        xaxis=np.arange(1, obj[2].data.shape[1],1)
                        yaxis=obj[2].data[line,1:obj[2].data.shape[1]]
                        plt.figure(figsize=(16.0,8.0))
                        ax1=plt.subplot(211)
                        ax1.imshow(obj[2].data, origin='lower',cmap='afmhot',
                                   vmin=np.percentile(obj[2].data,1),
                                   vmax=np.percentile(obj[2].data,99), aspect='auto')
                        ax1.axhline(y=line, linestyle='--', color='red',linewidth=2., alpha=0.7)
                        ax1.set_ylabel('Position Along Slit', fontsize=14)
                        ax2=plt.subplot(212)
                        ax2.plot(xaxis, yaxis, color='red' )
                        ax2.set_xlim(left=np.min(xaxis), right=np.max(xaxis))
                        ax2.set_ylabel('Counts', fontsize=14)
                        ax2.set_xlabel('Dispersion Axis', fontsize=14)
                        plt.show()

                        print('')
                        answer3 = raw_input('Do you wish to interpolate another bad column? (y/n) ' )

                        if answer3=='n':
                            break
                        if answer3=='y':
                            print('')
                        else:
                            print('Please, type y or n ')

                    except(NameError, SyntaxError,IndexError):
                            print('')
                            print("Check if you typed a correct line number. ")
                break
            else:
                print('Please, type y or n ')

        except(NameError, SyntaxError,IndexError):
                print('')
                print("Check if you typed a correct line number. ")


def obj_transf_obj():
    """ Transform science object frame. """

    print('# TRANSFORMING SCIENCE SPECTRUM #')

    # Remove pre-existing processed files.
    if os.path.exists('tbcgsqgemgs{}'.format(obj_sci_name[0])):
        os.remove('tbcgsqgemgs{}'.format(obj_sci_name[0]))

    gmos.gstransform.unlearn() # Debug gstransform.
    # Task parameters.
    gstransformFlags={'wavtranam':'gs{}'.format(arc_sci_name[0]),
                    'fl_vardq':'yes'}
    # Transform spectrum.
    gmos.gstransform('bcgsqgemgs{}'.format(obj_sci_name[0]), **gstransformFlags) # IRAF task gstransform.

def obj_sky_sub_obj():
    """ Subtract sky background from science object frame.
        Print raw and sky subtracted frames for comparison. """

    print('# SKY-SUBTRACTING #')

    # Remove pre-existing processed files.
    if os.path.exists('stbcgsqgemgs{}'.format(obj_sci_name[0])):
        os.remove('stbcgsqgemgs{}'.format(obj_sci_name[0]))

    gmos.gsskysub.unlearn() # Debug gsskysub.
    # Task parameters.
    gsskysubFlags={'fl_int':'no'}
    # Subtract sky background.
    gmos.gsskysub('tbcgsqgemgs{}'.format(obj_sci_name[0]), **gsskysubFlags) # IRAF task gsskysub.

    # Print frames with and without sky correction.
    obj=fits.open('tbcgsqgemgs{}'.format(obj_sci_name[0]))
    subobj=fits.open('stbcgsqgemgs{}'.format(obj_sci_name[0]))

    obj_data = obj[2].data
    subobj_data = subobj[2].data
    obj_shape = obj_data.shape
    subobj_shape = subobj_data.shape
    plt.figure(figsize=(16.0,8.0))
    plt.subplot(2, 1, 1)
    plt.imshow(obj[2].data, origin='lower',cmap='afmhot',
                   vmin=np.percentile(obj[2].data,5),
                   vmax=np.percentile(obj[2].data,90), aspect='auto')
    plt.ylabel('Position Along Slit', fontsize=14)
    plt.subplot(2, 1, 2)
    plt.imshow(subobj[2].data, origin='lower',cmap='afmhot',
                   vmin=np.percentile(subobj[2].data,5),
                   vmax=np.percentile(subobj[2].data,90), aspect='auto')
    plt.xlabel('Dispersion Axis', fontsize=14)
    plt.ylabel('Position Along Slit', fontsize=14)
    plt.tight_layout(w_pad=-0.9)
    plt.suptitle('Pre- and Post- Sky Subtraction', y=1.0)
    plt.savefig('skysub-obj-{}.png'.format(obj_sci_name[0]))
    plt.show()
    plt.clf()
    plt.close()

def obj_extract_obj():
    """ Extract science object spectrum.
        Print position of extracted spectrum for checking. """

    print('# EXTRACTING SCIENCE SPECTRUM #')

    # Remove pre-existing extraction info file in the database directory.
    if os.path.exists('database/apstbcgsqgemgs{}_SCI_1_'.format(obj_sci_name[0].replace('.fits',''))):
        os.remove('database/apstbcgsqgemgs{}_SCI_1_'.format(obj_sci_name[0].replace('.fits','')))

    # Remove pre-existing extracted spectrum.
    if os.path.exists('estbcgsqgemgs{}'.format(obj_sci_name[0])):
        os.remove('estbcgsqgemgs{}'.format(obj_sci_name[0]))

    gmos.gsextract.unlearn() # Debug gsextract.
    # Task parameters.
    gsextractFlags={'fl_inter':'no', 'apwidth':'4', 'torder':'20'}
    # Extract spectrum.
    gmos.gsextract('stbcgsqgemgs{}'.format(obj_sci_name[0]), **gsextractFlags) # IRAF task gsextract.

    # Row position of extracted spectrum in the science object frame.
    center = np.genfromtxt('database/apstbcgsqgemgs{}_SCI_1_'.format(obj_sci_name[0].replace('.fits','')), skip_header=5,
                        max_rows=1, usecols=2, invalid_raise=False)

    # Load science object frame.
    obj=fits.open('stbcgsqgemgs{}'.format(obj_sci_name[0]))
    obj_data = obj[2].data
    obj_shape = obj_data.shape

    # Print frame with row of extracted spectrum.
    fig = plt.figure(figsize=(14.0,6.0))
    ax1 = fig.add_subplot(111)
    plt.imshow(obj[2].data, origin='lower',cmap='afmhot',
                   vmin=np.percentile(obj[2].data,5),
                   vmax=np.percentile(obj[2].data,90), aspect='auto')
    ax1.axhline(y=center, linestyle='--', color='red',linewidth=2., alpha=0.7)
    plt.tight_layout(w_pad=-0.9)
    plt.ylabel('Position Along Slit', fontsize=14)
    plt.xlabel('Dispersion Axis', fontsize=14)
    plt.suptitle('Extracted Spectrum Position', y=1.0, fontsize=14)
    plt.savefig('extract_obj_{}.png'.format(obj_sci_name[0]))
    plt.show()
    plt.clf()
    plt.close()

    # Check if the spectrum position is correct.
    # Select another row to extract the spectrum.
    while True:
        print('')
        answer1 = raw_input('Are you satisfied with the extracted spectrum position? [y/n]')
        if answer1 == "y":
            break

        if answer1 == "n":
            print('')
            answer2 = raw_input('Type the new row position for extracting the spectrum: ')

            # Remove extraction info (last) file in the database directory.
            os.remove('database/aplast')
            # Remove extracted spectrum.
            os.remove('estbcgsqgemgs{}'.format(obj_sci_name[0]))

            # Open extraction info file in the database directory.
            lines = open('database/apstbcgsqgemgs{}_SCI_1_'.format(obj_sci_name[0].replace('.fits',''))).read().splitlines()
            lines[5] = '	center	1566. {}'.format(answer2)
            # Write new selected row to extract spectrum.
            open('database/apstbcgsqgemgs{}_SCI_1_'.format(obj_sci_name[0].replace('.fits','')),'w').write('\n'.join(lines))

            gmos.gsextract.unlearn() # Debug gsextract.
            # Task parameter.
            gsextractFlags={'fl_inter':'no', 'apwidth':'4', 'torder':'20'}
            # Extract spectrum.
            gmos.gsextract('stbcgsqgemgs{}'.format(obj_sci_name[0]), **gsextractFlags) # IRAF task gsextract.

            # Row position of extracted spectrum in the science object frame.
            center = np.genfromtxt('database/apstbcgsqgemgs{}_SCI_1_'.format(obj_sci_name[0].replace('.fits','')), skip_header=5,
                        max_rows=1, usecols=2, invalid_raise=False)

            # Load standard star frame.
            obj=fits.open('stbcgsqgemgs{}'.format(obj_sci_name[0]))
            obj_data = obj[2].data
            obj_shape = obj_data.shape

            # Print frame with row of extracted spectrum.
            fig = plt.figure(figsize=(14.0,6.0))
            ax1 = fig.add_subplot(111)
            plt.imshow(obj[2].data, origin='lower',cmap='afmhot',
                           vmin=np.percentile(obj[2].data,5),
                           vmax=np.percentile(obj[2].data,90), aspect='auto')
            ax1.axhline(y=center, linestyle='--', color='red',linewidth=2., alpha=0.7)
            plt.tight_layout(w_pad=-0.9)
            plt.ylabel('Position Along Slit', fontsize=14)
            plt.xlabel('Dispersion Axis', fontsize=14)
            plt.suptitle('Extracted Spectrum Position', y=1.0, fontsize=14)
            plt.savefig('extract_obj-{}.png'.format(obj_sci_name[0]))
            plt.show()
            plt.clf()
            plt.close()

        else:
            print("Type y or n")

    # Load extracted science object spectrum.
    obj=fits.open('estbcgsqgemgs{}'.format(obj_sci_name[0]))
    obj_header = obj[2].header
    obj_data = obj[2].data
    obj_shape = obj_data.shape
    crval = obj_header['CRVAL1']
    cd1_1 = obj_header['CD1_1']

    # Print extracted standard star spectrum
    fig, ax = plt.subplots(figsize=(14.0,6.0))
    plt.plot(crval + cd1_1*np.arange(1,len(obj[2].data)+1,1), obj[2].data, linewidth=0.55)
    ax.xaxis.set_major_locator(MultipleLocator(500))
    ax.xaxis.set_minor_locator(MultipleLocator(50))
    ax.set_ylim(np.percentile(obj[2].data,5), np.percentile(obj[2].data,95))
    plt.ylabel('Counts', fontsize=14)
    plt.xlabel(r'Wavelength $\ [\AA]$', fontsize=14)
    plt.title('Extracted Spectrum', fontsize=14)
    plt.tight_layout(w_pad=-0.9)
    plt.savefig('extracted_spec_obj{}.png'.format(obj_sci_name[0]))
    plt.show()
    plt.clf()
    plt.close()

def obj_calib_obj():
    """ Calibrate science object spectrum.
        Plot calibrated spectrum of the science object. """

    print('# CALIBRATING SCIENCE SPECTRUM # ')

    # Remove pre-existing calibrated spectrum.
    if os.path.exists('cestbcgsqgemgs{}'.format(obj_sci_name[0])):
        os.remove('cestbcgsqgemgs{}'.format(obj_sci_name[0]))

    gmos.gscalibrate.unlearn() # Debug gscalibrate.
    # Calibrate standard star spectrum.
    calibrateFlags={'observatory':'gemini-south'}
    gmos.gscalibrate('estbcgsqgemgs{}'.format(obj_sci_name[0]), **calibrateFlags ) # IRAF task gscalibrate.

    # Load calibrated spectrum.
    obj=fits.open('cestbcgsqgemgs{}'.format(obj_sci_name[0]))
    obj_header = obj[2].header
    obj_data = obj[2].data
    obj_shape = obj_data.shape
    crval = obj_header['CRVAL1']
    cd1_1 = obj_header['CD1_1']

    # Plot calibrated spectrum of the science object.
    fig, ax = plt.subplots(figsize=(14.0,6.0))
    plt.plot(crval + cd1_1*np.arange(1,len(obj[2].data)+1,1), obj[2].data, linewidth=0.55)
    plt.grid(alpha=0.8, ls='--')
    ax.xaxis.set_major_locator(MultipleLocator(500))
    ax.xaxis.set_minor_locator(MultipleLocator(50))
    ax.set_ylim(np.percentile(obj[2].data,5), np.percentile(obj[2].data,95))
    plt.ylabel('Flux [ergs cm$^{-2}$ s$^{-1}$ $\ \AA$$^{-1}$] ', fontsize=14)
    plt.xlabel(r'Wavelength $\ [\AA]$', fontsize=14)
    plt.title('Calibrated Spectrum', fontsize=14)
    plt.xticks(fontsize = 11)
    plt.yticks(fontsize = 11)
    plt.tight_layout(w_pad=-0.9)
    plt.savefig('calib-spec-obj-{}.png'.format(obj_sci_name[0]))
    plt.show()
    plt.clf()
    plt.close()

def obj_despike_obj():
    """ Use the modified z-score detection of outlying points
        to exclude bad pixels and spikes from the spectrum. """

    while True:
        print('')
        answer = raw_input('Do you wish to remove spikes in your spectrum? ')

        if answer == 'n':

            break

        if answer == 'y':
            # Load calibrated spectrum.
            obj=fits.open('cestbcgsqgemgs{}'.format(obj_sci_name[0]))
            obj_header = obj[2].header
            obj_data = obj[2].data
            obj_shape = obj_data.shape
            crval_obj = obj_header['CRVAL1']
            cd1_1_obj = obj_header['CD1_1']
            intensity = obj[2].data
            wavelength = crval_obj + cd1_1_obj*np.arange(1,len(intensity)+1,1)

            ## Whitaker and Hayes' modified Z-score based approach for spike detection
            ## in spectra.

            def modified_z_score(intensity):
                median_int = np.median(intensity)
                mad_int = np.median([np.abs(intensity - median_int)])
                modified_z_scores = 0.6745 * (intensity - median_int) / mad_int
                return modified_z_scores

            delta_int = np.diff(intensity)

            threshold = 7 #z-score threshold.

            intensity_modified_z_score=np.array(np.abs(modified_z_score(delta_int)))

            # Print the modified z-score of Delta X (i) for the points along the spectrum.
            fig, ax = plt.subplots(figsize=(14.0,6.0))
            plt.plot(wavelength[1:], intensity_modified_z_score)
            plt.plot(wavelength[1:], threshold*np.ones(len(wavelength[1:])), label = 'threshold = {}'.format(threshold))
            plt.title('Modified z-Score of Delta x (i) [Whitaker and Hayes Approach ]', fontsize = 15)
            plt.xticks(fontsize = 15)
            plt.yticks(fontsize = 15)
            plt.xlabel('Wavelength ', fontsize = 15)
            plt.ylabel('|z-scores|', fontsize = 15)
            plt.legend()
            # plt.savefig('z_scores.png')
            plt.show()

            # 1 is assigned to spikes, 0 to non-spikes:
            spikes = abs(np.array(modified_z_score(intensity))) > threshold

            # Print the detected spikes along the spectrum.
            fig, ax = plt.subplots(figsize=(14.0,6.0))
            plt.plot(wavelength, spikes, color = 'red')
            plt.title('Spikes: ' + str(np.sum(spikes)), fontsize = 15)
            plt.grid()
            plt.xticks(fontsize = 15)
            plt.yticks(fontsize = 15)
            plt.xlabel( 'Wavelength' ,fontsize = 15)
            # plt.savefig('z_score_spikes.png')
            plt.show()

            # Delete the spikes and fix the spectrum.
            def fixer(y,m):
                threshold = 7
                spikes = abs(np.array(modified_z_score(np.diff(y)))) > threshold
                y_out = y.copy()

                for i in np.arange(len(spikes)):
                    if spikes[i] != 0:
                        w = np.arange(i - m, i + 1 + m)
                        w2 = w[spikes[w] == 0]
                        y_out[i] = np.mean(y[w2])
                return y_out

            # Print a comparison between the original and fixed spectrum.
            fig, ax = plt.subplots(figsize=(14.0,6.0))
            plt.plot(wavelength, intensity, 'darkgrey',linewidth=0.55, label = 'Original Spectrum')
            ax.xaxis.set_major_locator(MultipleLocator(500))
            ax.xaxis.set_minor_locator(MultipleLocator(50))
            plt.plot(wavelength, fixer(intensity,m=3), alpha=0.85, linewidth=0.55, label = 'Fixed Spectrum')
            ax.set_ylim(np.percentile(intensity,5), np.percentile(intensity,95))
            plt.grid(alpha=0.8, ls='--')
            plt.ylabel('Flux [ergs cm$^{-2}$ s$^{-1}$ $\ \AA$$^{-1}$] ', fontsize=14)
            plt.xlabel(r'Wavelength $\ [\AA]$', fontsize=14)
            plt.title('Calibrated Spectrum', fontsize=14)
            plt.xticks(fontsize = 11)
            plt.yticks(fontsize = 11)
            plt.tight_layout(w_pad=-0.9)
            plt.legend()
            plt.show()

            # Print the fixed spectrum.
            fig, ax = plt.subplots(figsize=(14.0,6.0))
            plt.plot(wavelength, fixer(intensity,m=3),alpha=0.85, linewidth=0.55)
            ax.xaxis.set_major_locator(MultipleLocator(500))
            ax.xaxis.set_minor_locator(MultipleLocator(50))
            ax.set_ylim(np.percentile(intensity,5), np.percentile(intensity,95))
            plt.grid(alpha=0.8, ls='--')
            plt.ylabel('Flux [ergs cm$^{-2}$ s$^{-1}$ $\ \AA$$^{-1}$] ', fontsize=14)
            plt.xlabel(r'Wavelength $\ [\AA]$', fontsize=14)
            plt.title('Calibrated Spectrum', fontsize=14)
            plt.xticks(fontsize = 11)
            plt.yticks(fontsize = 11)
            plt.tight_layout(w_pad=-0.9)
            plt.legend()
            plt.show()

            break
        else:
            print('')
            print "Type y or n"
            print('')

# Call the reduction functions.

while True:
    # Check if the calibration sensitivity functions is already available in
    # the directory.
    if os.path.exists('sens.fits'):
        print('The file SENS.FITS is already available in the current directory. ')
        print('')
        # Ask if the user wants to remake the reduction of the standard star file.
        answer = raw_input('Do you wish to REMAKE the reduction of the STANDARD STAR file? [y/n] ')

        if answer == "n":

            break

        if answer == "y":
            # Remove pre-existing sensitivity function files.
            if os.path.exists('std'):
                os.remove('std')
            if os.path.exists('sens.fits'):
                os.remove('sens.fits')

            selec_std()

            print "------------------------------"
            print "# REDUCTION OF STANDARD STAR #"
            print "------------------------------"
            # Call standard star reduction functions.
            std_gbias()
            std_reduc_arc()
            std_wavelength_arc()
            std_transf_arc()
            std_reduc_flat()
            std_qecorr_flat()
            std_gmosaic_flat()
            std_masterflat()
            std_reduc1_std()
            std_gemfix_std()
            std_qecorr_std()
            std_reduc2_std()
            std_badcolumn_std()
            std_transf_std()
            std_sky_sub_std()
            std_extract_std()
            std_calib_std()

            break

        else:
            print('')
            print("Type y or n")
            print('')
    else:
        # Call standard star reduction functions.
        selec_std()
        std_gbias()
        std_reduc_arc()
        std_wavelength_arc()
        std_transf_arc()
        std_reduc_flat()
        std_qecorr_flat()
        std_gmosaic_flat()
        std_masterflat()
        std_reduc1_std()
        std_gemfix_std()
        std_qecorr_std()
        std_reduc2_std()
        std_badcolumn_std()
        std_transf_std()
        std_sky_sub_std()
        std_extract_std()
        std_calib_std()

        print "--------------------------------------"
        print "# END OF THE STANDARD STAR REDUCTION #"
        print "--------------------------------------"

        break

# Call science object reduction functions.

selec_obj()

print "-------------------------------"
print "# REDUCTION OF SCIENCE OBJECT #"
print "-------------------------------"

obj_gbias()
obj_reduc_arc()
obj_wavelength_arc()
obj_transf_arc()
obj_reduc_flat()
obj_qecorr_flat()
obj_gmosaic_flat()
obj_masterflat()
obj_reduc1_obj()
obj_gemfix_obj()
obj_qecorr_obj()
obj_reduc2_obj()
obj_badcolumn_obj()
obj_transf_obj()
obj_sky_sub_obj()
obj_extract_obj()
obj_calib_obj()
obj_despike_obj()

print '#------------------#'

print '# END OF REDUCTION #'

print '#------------------#'
