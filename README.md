# GMOS-SPiKE
GMOS Spectral reduction Pipeline for Kilonova Events

Author: Thallis Pessi (thallis.pessi@gmail.com)

# About the pipeline
This pipeline was created as part of an effort to detect the optical counterpart of gravitational wave events with the GMOS instrument at the Gemini Observatory. The pipeline provides a fast and automated reduction of longslit spectra obtained with GMOS. Although refined for the reduction of kilonova signals, the pipeline can be used for the treatment of different types of spectra observed with the GMOS in mode longslit with minor changes on its parameters.

This work is the result of a master's thesis project entitled 'A Spectroscopic Data Reduction Pipeline for Optical Observations of Kilonovae', developed at Universidade Federal de Santa Maria with the support of the CAPES scholarship. 

Feedback and comments are welcome!

# Dependencies
GMOS-SPiKE makes use of PyRAF, using different Python packages with IRAF reduction tools. The pipeline uses the following Python packages: numpy, pyraf, os, astropy and matplotlib. These packages can all be installed through the ```conda install``` command.

The pipeline needs to be run on a geminiconda environment, which can be installed with the following commands:

```
conda config --add channels http://astroconda.gemini.edu/public
create -n geminiconda python=2.7 iraf-all pyraf-all stsci gemini
```

The geminiconda environment provides the GEMINI IRAF packages needed for the reduction of GMOS data. The pipeline uses the following GEMINI IRAF packages: gbias, gsreduce, gswavelength, gstransform, gqecorr, gmosaic, gsflat, gemfix, gsskysub, gsextract, gsstandard and gscalibrate. 

The pipeline was succesfully tested with python2.7 on Linux systems.

# Usage
The pipeline must be run in a directory containing a 'raw' file with the bias, flat, arc, science and standard star data obtained with the GMOS. The path of the 'raw' directory can be modified in the script. The pipeline can be run using:

```
python gmos-spike.py
```
The pipeline is divided in two blocks: the reduction of the standard star spectrum and the reduction of the science object, for which the sensitivity function from the standard star is applied. First, the pipeline reads through the files at the 'raw' directory and prints the available values of the central wavelength for the standard star spectra. The user must type the preferred central wavelength and the pipeline then selects the files of bias, flat, lamp and observed spectrum that match that value. The same is done for the science object.   

# Output
The main output of the reduction process is the science spectrum, corrected by bias, flat, quantum efficiency, bad pixels, bad columns, excessive noise and calibrated by wavelength and flux. Other files produced by the intermediate steps of the process are also available as output. The prefix of their names indicate the reduction step and the GEMINI IRAF package that produced the file:
        
        PACKAGE PREFIX FUNCTION
      - gsreduce    gs             Subtract bias, apply overscan and cosmic ray correction 
      - gemfix      gemgs          Improve cosmic ray and bad pixel correction
      - gqecorr     qgemgs         Apply quantum efficiency correction
      - gsreduce    gsqgemgs       Apply flat field correction 
      - fixpix      bcgsqgemgs     Interpolate bad columns
      - gstransform tbcgsqgemgs    Apply wavelength calibration
      - gsskysub    stbcgsqgemgs   Subtract sky background 
      - gsextract   estbcgsqgemgs  Extract spectrum
      - gscalibrate cestbcgsqgemgs Calibrate spectrum
       

# License 
GMOS-SPiKE operates under the MIT license. Please, check the LICENSE file for more information.

