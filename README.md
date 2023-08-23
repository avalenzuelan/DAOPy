# DAOpy

This is a Python wrapper to use DAOPHOT (Stetson 1987) and ALLSTAR/ALLFRAME (Stetson 1994) Fortran PSF-fitting photometry softwares in Python environments.

The idea is that you can iterate over a lot of images using Python with the power of a high quality, reliable photometric software such as DAOPHOT.

## DAOPHOT in a nutshell

DAOPHOT/ALLSTAR/ALLFRAME softwares use a configuration file with extention .opt, that contains all the information regarding the images, fitting procedures, apertures, tolerances, etc. If there is a .opt file in the folder where you execute DAOPHOT, it reads it. If not, it will ask for all the parameters one by one. DAOpy handles this creating the .opt files reading a .json file, containing all keywords necessary to start the softwares.

The procedure of DAOPHOT is pretty straight forward: