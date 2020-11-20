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
conda config --add channels http://ssb.stsci.edu/astrocondaconda
create -n geminiconda python=2.7 iraf-all pyraf-all stsci gemini
```

The geminiconda environment provides the GEMINI IRAF packages needed for the reduction of GMOS data. The pipeline uses the following GEMINI IRAF packages: gbias, gsreduce, gswavelength, gstransform, gqecorr, gmosaic, gsflat, gemfix, gsskysub, gsextract, gsstandard and gscalibrate. 

The pipeline was succesfully tested with python2.7 on Linux systems.

#Usage
The pipeline must be run in a directory containing a 'raw' file with the bias, flat, arc, science and standard star data obtained with the GMOS. The path of the 'raw' directory can be modified in the script. The pipeline is run using:

```
python gmos-spike.py
```

#License 
GMOS-SPiKE operates under the MIT license. Please, check the LICENSE file for more information.

