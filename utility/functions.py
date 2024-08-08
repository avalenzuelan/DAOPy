#author: Álvaro Valenzuela Navarro <auvalenzuela at uc.cl>

#Functions for DAOPy
#This file contains the functions used in DAOPy, such as the ones
#used to read output of DAOPHOT, ALLFRAME, DAOMATCH, etc.

import numpy as np
import os
import sys
import pandas as pd
from astropy.io import fits
from astropy.wcs import WCS

def read_alf(path, filename):
    """  
    This function reads the output of ALLFRAME and returns a pandas dataframe
    with the information of the sources detected in the image.
    """

    df = pd.read_csv(os.path.join(path, filename),
                        skiprows=3,
                        names=['ID', 'X', 'Y', 'mag', 'Emag', 'SKY', \
                               'ITER', 'CHI', 'SHARP'],
                        delim_whitespace=True)
    return df

def read_mag(path, filename):
    """  
    This function reads the output of ALLFRAME and returns a pandas dataframe
    with the information of the sources detected in the image.
    """

    df = pd.read_csv(os.path.join(path, filename),
                        skiprows=3,
                        names=['ID', 'X', 'Y', 'mag', 'Emag', 'ext_std', \
                               'NFRAMES', 'CHI', 'SHARP', 'VAR-INDEX', \
                               'BLUNDER-INDEX'],
                        delim_whitespace=True,
                        index_col=None)
    return df

def read_mtr(path, filename):
    """  
    This function reads the output of ALLFRAME and returns a pandas dataframe
    with the information of the sources detected in the image.
    """

    df = pd.read_csv(os.path.join(path, filename),
                        skiprows=3,
                        names=['ID', 'X', 'Y', 'mag', 'Emag', 'ext_std', \
                               'NFRAMES', 'CHI', 'SHARP', 'VAR-INDEX', \
                               'BLUNDER-INDEX', 'ID_in', 'dX', 'dY', \
                                'IDK1', 'IDK2'],
                        usecols=['ID', 'X', 'Y', 'mag', 'Emag', 'ext_std', \
                                 'NFRAMES', 'CHI', 'SHARP', 'VAR-INDEX', \
                                 'BLUNDER-INDEX'],
                        delim_whitespace=True,
                        index_col=None)
    return df

def read_addstar_input(path, 
                       filename, 
                       mag='MAG'):
    """ 
    This function reads the input file for ADDSTAR and returns a pandas
    dataframe with the information of the sources to be added to the image.
    """
    df = pd.read_csv(os.path.join(path, filename),
                    skiprows=[0],
                    names=['ID_in', 'X_in', 'Y_in', mag],
                    delim_whitespace=True,
                    index_col='ID_in')
    return df

def add_coordinates_df(df, 
                       path_to_fits,
                       x='X',
                       y='Y',
                       out_suffix=''):
    """ 
    This function reads a dataframe with the information of the sources in a 
    catalogue that has the columns 'X' and 'Y'. Then, adds the columns 'RA' and
    'DEC' to the dataframe, which are the coordinates of the sources in the
    image. The coordinates are calculated using the WCS information of the
    image.
    """
    hdulist = fits.open(path_to_fits)
    header  = hdulist[0].header
    wcs     = WCS(header)
    coords  = wcs.pixel_to_world(df[x], df[y])
    ra_str, dec_str = 'RA' + out_suffix, 'DEC' + out_suffix
    df[ra_str], df[dec_str] = coords.ra.value, coords.dec.value
    return df

def read_sim(path, filename):
    """ 
    This function reads the output of CataXcorr with the simulated sources and
    output ones from ALLFRAME and returns a pandas dataframe with the 
    information of the sources detected in the image.
    """
    names = ['ID_in', 'X_in', 'Y_in', 'mag_in', 'ID_out', 'X_out', 'Y_out',
             'mag_out', 'emag_out', 'CHI_out', 'SHARP_out']
    df = pd.read_csv(os.path.join(path, filename),
                     names=names,
                     skiprows=4,
                     delim_whitespace=True,
                     na_values=99.999)
    return df

def running_median(x, y, num_bins=None, bins=None):
    if bins is None:
        bins = np.linspace(np.min(x), np.max(x), num_bins + 1)
    else:
        num_bins = len(bins) - 1

    median_values = np.zeros(num_bins)
    mad_values = np.zeros(num_bins)
    for i in range(num_bins):
        mask = (x >= bins[i]) & (x < bins[i + 1])
        median_values[i] = np.median(y[mask])
        mad_values[i] = np.median(np.abs(y[mask] - median_values[i]))

    return median_values, mad_values
                     
def get_header_daophot_files(filename):
    f = open(filename, 'r')
    count = 0
    header = []
    for line in f:
        header.append(line.strip().split())
        count += 1
        if count > 1:
            return header
        
def save_dataframe(df, path_to_save, line):
    df.to_csv(path_to_save, index=False, sep="\t", header=0)

    def line_prepender(path_to_save, line): #Got this from StackOverflow
        with open(path_to_save, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(line.rstrip('\r\n') + '\n\n' + content)
        return
    
    line_prepender(path_to_save, line)
    return