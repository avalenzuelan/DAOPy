#author: Álvaro Valenzuela Navarro <auvalenzuela at uc.cl>
#version: 0.1   2023-05-25: Creation of the file
#version: 0.2   2023-05-26: Creation of FitsImage class
#version: 0.3   2023-05-27: Creation of DaophotExecution class
#version: 0.4   2023-05-28: Creation of OPTFiles class
#version: 0.5   2023-05-29: Creation of AllstarExecution class
#version: 0.6   2023-05-30: Creation of AllframeExecution class

import pandas as pd
import astropy.io.fits as fits
import numpy as np
import json
import os

class FitsImage():

    def __init__(self, path_to_folder, fits_filename, extension = 0,
                 field_name=None, texp=None, chip=None, filter=None) -> None:
        
        self.fits_filename = fits_filename
        self.filename = self.fits_filename.split('.')[0]
        self.path_to_folder = path_to_folder
        self.path_to_fits = os.path.join(path_to_folder, fits_filename)
        self.texp = texp
        self.filter = filter
        self.field_name = field_name
        self.data = self._open_data(self.path_to_fits, ext= extension)
        self.header = self._open_header(self.path_to_fits, ext = extension)
        self._ron = self._get_ron()
        self._gain = self._get_gain()

    def _open_data(self, path_to_fits, ext = 0):
        print('--- Opening %s' % path_to_fits)
        hdulist = fits.open(path_to_fits)
        return hdulist[ext].data
    
    def _open_header(self, path_to_fits, ext = 0):
        hdulist = fits.open(path_to_fits)
        return hdulist[ext].header
    
    def _get_ron(self):
        return self.header['READNOIS']
    
    def _get_gain(self):
        return self.header['GAIN']
    
    @property
    def ron(self):
        return self._ron
    
    @ron.setter
    def ron(self, value):
        self._ron = value

    @property
    def gain(self):
        return self._gain
    
    @gain.setter
    def gain(self, value):
        self._gain = value

    
class OPTFiles():

    """ .OPT Files   
    
    This class manages the creation and edition of .opt files needed for
    to use DAOPHOT, ALLSTAR and ALLFRAME. The parameters are read from a 
    .json file, and can be editted later with the setter method .params """

    def __init__(self, path_to_folder, filename) -> None:
        self.path_to_folder = path_to_folder
        self.filename = filename
        self.json_path = os.path.join(self.path_to_folder, 
                                      self.filename)
        self._params = self._open_json(self.json_path)

    def _open_json(self, path_to_json):
        with open(path_to_json, 'r') as f:
            data = json.load(f)
        return data
    
    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, args):
        opt, key, value = args
        self._params[opt][key] = value

    def create_opt_files(self, path_to_opts = '.'):
        for opt_filename, opt_params in self.params.items():
            path_to_save_opt = os.path.join(path_to_opts, 
                                            opt_filename + '.opt')
            
            with open(path_to_save_opt, 'w') as f:
                #print(opt_filename+'\n', opt_params)
                for key, param in opt_params.items():
                    f.write(key + ' = ' + str(param) + '\n')
                f.close()
        return True
    
class DaophotExecution():

    """DAOPHOT Execution.

    This class manages the creation of the input commands for DAOPHOT and
    its execution. It works in a way that preserves the flexibility of using
    DAOPHOT directly, but making it suitable to create pipelines.

    Parameters
    ----------
    path_to_folder : str
        The relative or absolute path to the folder where the images are stored.

    filename : str
        The name of the file of the image WITHOUT the extension.
    
    summed : int, default=1
        The number of frames summed to create the input image

    averaged : int, default=1
        The number of frames averaged to create the input image

    """

    def __init__(self, 
                 path_to_folder, 
                 filename, 
                 summed=1, 
                 averaged=1,
                 niter_psf=2
                 ):
        
        self.filename = filename #create a setter for this
        self.path_to_folder = path_to_folder
        self.summed = summed
        self.averaged = averaged
        self.niter_psf = niter_psf
        self.mycwd = os.getcwd()
        self.calling_sequence = ''
        self.old_calling_sequence = []

    def attach_image(self, filename):
        self.calling_sequence += 'at ' + filename + '\n'
        return True
    
    def remove_files(self, extention):
        os.chdir(self.path_to_folder)
        os.system('rm ' + self.filename + extention)
        os.chdir(self.mycwd)
        return True

    def find_stars(self, delete=True, filename_ow='x.coo'): #Añadir opción para cambiar el threshold on the fly?
        if delete:
            self.remove_files('.coo')
            self.calling_sequence += 'find\n' + str(self.summed) + ',' + \
            str(self.averaged) + '\n\ny\n'
        else:
            self.calling_sequence += 'find\n' + str(self.summed) + ',' + \
            str(self.averaged) + '\n\n'+filename_ow+'y\n'
        return True

    def aperture_phot(self, delete=True, filename_ow='x.ap'): #ow stands for overwrite
        if delete:
            self.remove_files('.ap')
            self.calling_sequence += 'phot\n\n\n\n\n'
        else:
            self.calling_sequence += 'phot\n\n\n\n' + filename_ow + '\n'
        return True
    
    def pick_stars(self, nstars, lim_mag, delete=True, filename_ow='x.lst'):
        if delete:
            self.remove_files('.lst')
            self.calling_sequence += 'pick\n\n' + str(nstars) + ',' + \
            str(lim_mag) + '\n\n'
        else:
            self.calling_sequence += 'pick\n\n' + str(nstars) + ',' + \
            str(lim_mag) + '\n' + filename_ow + '\n'
        return True
    
    def psf_model(self, 
                  ap_name = None,
                  lst_name = None,
                  psf_name = None,
                  nei_name = None,
                  delete=True, 
                  filename_ow='x.psf'):
        if ap_name is None:
            ap_name = self.filename + '.ap'
        if lst_name is None:
            lst_name = self.filename + '.lst'
        if psf_name is None:
            psf_name = self.filename + '.psf'
        if nei_name is None:
            nei_name = self.filename + '.nei'

        if delete:
            self.remove_files('.psf')
            self.calling_sequence += 'psf\n' + ap_name + '\n' + lst_name + \
                '\n' + psf_name +'\n' + nei_name + '\n'
            print(self.calling_sequence)
        else:
            self.calling_sequence += 'psf\n' + ap_name + '\n' + lst_name + \
                '\n' + psf_name + '\n' + nei_name + '\n'
            print(self.calling_sequence)
        return True

    def substar(self, delete=True, filename_ow='xs.fits'):
        if delete:
            self.remove_files('.nei')
            self.calling_sequence += 'substar\n\n' + self.filename + \
                '.nei\ny\n\n\n'
        else:
            self.calling_sequence += 'substar\n\n' + self.filename + \
            '.nei\ny\n\n' + filename_ow  +'\n'
        return
    
    def iter_psf(self, delete=True, filename_ow='x.psf'):
        """ 
        This routine executes the PSF routine iteratively, using the .nei file
        as input for the PSF routine. It is useful to improve the PSF model
        iteratively in crowded fields. 
        """
        #TBD

        return
    
    def execute(self):
        """ Execute DAOPHOT command sequence

        Routine that execute all commands previously stacked, and resets the
        calling sequence to an empty string.
        """
        os.chdir(self.path_to_folder)
        self.calling_sequence = 'daophot << EOF\n' + self.calling_sequence +\
                                ' EOF'
        os.system(self.calling_sequence)
        self.old_calling_sequence.append(self.calling_sequence)
        self.calling_sequence = ''
        os.chdir(self.mycwd)

class AllstarExecution():

    def __init__(self, 
                 path_to_folder, 
                 filename,
                 ):
        
        self.filename = filename
        self.path_to_folder = path_to_folder
        self.mycwd = os.getcwd()
        self.calling_sequence = ''
        self.old_calling_sequence = []
    
        
    def execute(self):
        """ Execute ALLSTAR command sequence

        Routine that execute all commands previously stacked, and resets the
        calling sequence to an empty string.
        """
        os.chdir(self.path_to_folder)
        self.calling_sequence = 'allstar << EOF\n' + self.calling_sequence +\
                                ' EOF'
        os.system(self.calling_sequence)
        self.old_calling_sequence.append(self.calling_sequence)
        self.calling_sequence = ''
        os.chdir(self.mycwd)
        return

class AllframeExecution():

    def __init__(self, 
                 path_to_folder, 
                 filename,
                 ):
        
        self.filename = filename
        self.path_to_folder = path_to_folder
        self.mycwd = os.getcwd()
        self.calling_sequence = ''
        self.old_calling_sequence = []

    def daomatch(self, delete=True, filename_ow='x.mch'):
        if delete:
            self.remove_files('.mch')
            self.calling_sequence += 'daomatch\n\n\n\n\n'
        else:
            self.calling_sequence += 'daomatch\n\n\n\n' + filename_ow + '\n'
        return True
        
    def execute(self):
        """ Execute ALLFRAME command sequence

        Routine that execute all commands previously stacked, and resets the
        calling sequence to an empty string.
        """
        os.chdir(self.path_to_folder)
        self.calling_sequence = 'allframe << EOF\n' + self.calling_sequence +\
                                ' EOF'
        os.system(self.calling_sequence)
        self.old_calling_sequence.append(self.calling_sequence)
        self.calling_sequence = ''
        os.chdir(self.mycwd)
        return