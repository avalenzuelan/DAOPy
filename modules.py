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

    def __init__(self, 
                 path_to_folder, 
                 fits_filename, 
                 extension = 0,
                 field_name=None, 
                 texp=None, 
                 chip=None, 
                 filter=None):
        
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
        return True

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
                 path_to_folder : str, 
                 filename : str, 
                 summed=1, 
                 averaged=1,
                 ):
        
        self.filename = filename #create a setter for this
        self.path_to_folder = path_to_folder
        self.summed = summed
        self.averaged = averaged
        self.mycwd = os.getcwd()
        self.calling_sequence = ''
        self.old_calling_sequence = []

    def attach_image(self, filename=None):
        if filename is None:
            filename = self.filename
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
            str(self.averaged) + '\n\n'+filename_ow+'\ny\n'
        return True

    def aperture_phot(self, 
                      delete=True, 
                      filename_ow='x.ap'): #ow stands for overwrite
        if self.filename + '.psf' in os.listdir(self.path_to_folder):
            print('[WARNING] PSF file already exists.')
            print('[WARNING] Move or delete the  %s file before continue.' %\
                  (self.filename + '.psf'))
            return False
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
            str(lim_mag) + '\n' + filename_ow + '\n\n'
        return True
    
    def psf_model(self, 
                  ap_name = None,
                  lst_name = None,
                  psf_name = None,
                  nei_name = None,
                  delete=True):
        
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
        return

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

    def remove_files(self, extention):
        os.chdir(self.path_to_folder)
        os.system('rm ' + self.filename + extention)
        os.chdir(self.mycwd)
        return True
    
    def allstar(self,
                in_fits_name = None,
                psf_name = None,
                ap_name = None,
                als_name = None,
                sub_fits_name = None,
                delete = True):
        
        if in_fits_name is None:
            in_fits_name = self.filename
        if psf_name is None:
            psf_name = self.filename + '.psf'
        if ap_name is None:
            ap_name = self.filename + '.ap'
        if als_name is None:
            als_name = self.filename + '.als'
        if sub_fits_name is None:
            sub_fits_name = self.filename + 's.fits'

        if delete:
            self.remove_files('.als')
            self.calling_sequence += '\n' + in_fits_name + '\n' + psf_name + '\n' \
                + ap_name + '\n' + als_name + '\n' + sub_fits_name + '\n'
        else:
            self.calling_sequence += '\n' + in_fits_name + '\n' + psf_name + '\n' \
                + ap_name + '\n' + als_name + '\n\n' + sub_fits_name + '\n\n'
        return
        
    def execute(self):
        """ Execute ALLSTAR command sequence

        Routine that execute all commands previously stacked, and resets the
        calling sequence to an empty string.
        """
        os.chdir(self.path_to_folder)
        self.calling_sequence = 'allstar << EOF\n' + self.calling_sequence +\
                                'EOF'
        os.system(self.calling_sequence)
        print(self.calling_sequence)
        self.old_calling_sequence.append(self.calling_sequence)
        self.calling_sequence = ''
        os.chdir(self.mycwd)
        return

class DaomatchExecution():

    def __init__(self, 
                 path_to_folder : str, 
                 master_filename : str,
                 list_of_filenames : list
                 ):
        
        self.path_to_folder = path_to_folder
        self.master_filename = master_filename
        self.list_of_filenames = list_of_filenames
        self.str_of_filenames = '\n'.join(self.list_of_filenames)
        self.mycwd = os.getcwd()
        self.calling_sequence = ''
        self.old_calling_sequence = []

    def remove_files(self, extention, filename=None):
        if filename is None:
            filename = self.master_filename
        os.chdir(self.path_to_folder)
        os.system('rm ' + filename + extention)
        os.chdir(self.mycwd)
        return True

    def daomatch(self, delete=True, mch_name=None):
        if mch_name is None:
            mch_name = self.master_filename + '.mch'
        if delete:
            self.remove_files('.mch', filename=mch_name)
            self.calling_sequence += self.master_filename + '\n' + \
                mch_name + '\n' + self.str_of_filenames + '\n'
        else:
            self.calling_sequence += self.master_filename + '\n' + \
                mch_name + '\n\n' + self.str_of_filenames + '\n'
        return True
        
    def execute(self):
        """ Execute DAOMATCH command sequence

        Routine that execute all commands previously stacked, and resets the
        calling sequence to an empty string.
        """
        os.chdir(self.path_to_folder)
        self.calling_sequence = 'daomatch << EOF\n' + self.calling_sequence +\
                                ' EOF\n'
        os.system(self.calling_sequence)
        self.old_calling_sequence.append(self.calling_sequence)
        self.calling_sequence = ''
        os.chdir(self.mycwd)
        return
    
class DaomasterExecution():

    def __init__(self,
                 path_to_folder : str, 
                 mch_filename : str,
                 n_files : int
                 ):
        
        self.path_to_folder = path_to_folder
        self.mch_filename = mch_filename
        self.n_files = n_files
        self.mycwd = os.getcwd()
        self.calling_sequence = ''
        self.old_calling_sequence = []

    def remove_files(self, extention, filename=None):
        if filename is None:
            filename = self.mch_filename
        os.chdir(self.path_to_folder)
        os.system('rm ' + filename + extention)
        os.chdir(self.mycwd)
        return True

    def daomaster(self, delete=True, 
                  mch_name=None,
                  min_frac_enough=None,
                  max_sigma=None,
                  transform=None,
                  new_ids=True,
                  
                  ):
        
        if mch_name is None:
            mch_name = self.mch_filename
        if min_frac_enough is None:
            min_frac_enough = '2,1,1' 
        if max_sigma is None:
            max_sigma = '0.5' # Rodrigo's recommedation :)
        if transform is None:
            transform = '6'
        
        if delete:
            self.remove_files('.mag', filename=mch_name)
            self.remove_files('.cor', filename=mch_name)
            self.remove_files('.tfr', filename=mch_name)
            self.remove_files('.raw', filename=mch_name)
            self.calling_sequence += mch_name + '\n' + \
                min_frac_enough +'\n'+ \
                max_sigma + '\n' + \
                transform + '\n' + \
                '10' + self.n_files*'\n' + \
                '9\n8\n8\n7\n7\n6\n6\n5\n5\n4\n4\n3\n3\n2\n2\n1\n1\n1\n1\n0\n' + \
                'y\n' + \
                'y\n\n' + \
                'y\n\n' + \
                'y\n\n' + \
                'y\n\n\n' + \
                'y\n\n' + \
                'y\n' + (self.n_files + 1)*'\n' + \
                'y\n' + (self.n_files + 1)*'\n'
        return
    
    def execute(self):
        """ Execute DAOMASTER command sequence

        Routine that execute all commands previously stacked, and resets the
        calling sequence to an empty string.
        """
        os.chdir(self.path_to_folder)
        self.calling_sequence = 'daomaster << EOF\n' + self.calling_sequence +\
                                'EOF\n'
        os.system(self.calling_sequence)
        self.old_calling_sequence.append(self.calling_sequence)
        self.calling_sequence = ''
        os.chdir(self.mycwd)
        return

class AllframeExecution():

    def __init__(self,
                 path_to_folder : str,
                 mch_filename : str,
                 mag_filename : str):
        
        self.path_to_folder = path_to_folder
        self.mch_filename = mch_filename
        self.mag_filename = mag_filename
        self.mycwd = os.getcwd()
        self.calling_sequence = ''
        self.old_calling_sequence = []

    def remove_files(self, extention, filename=None, all_ext=False):
        if not all_ext:
            if filename is None:
                filename = self.mch_filename
            os.chdir(self.path_to_folder)
            os.system('rm ' + filename + extention)
            os.chdir(self.mycwd)
            return True
        elif all_ext:
            os.chdir(self.path_to_folder)
            os.system('rm *' + extention)
            os.chdir(self.mycwd)
            return True

    def allframe(self, delete=True, mch_name=None, mag_name=None):
        if mch_name is None:
            mch_name = self.mch_filename + '.mch'
        if mag_name is None:
            mag_name = self.mag_filename + '.mag'
        if delete:
            self.remove_files('.alf', all_ext=True)
            self.calling_sequence += '\n' + mch_name + '\n' + \
                mag_name + '\n'
        return
    
    def execute(self):
        """ Execute ALLFRAME command sequence

        Routine that execute all commands previously stacked, and resets the
        calling sequence to an empty string.
        """
        os.chdir(self.path_to_folder)
        self.calling_sequence = 'allframe << EOF\n' + self.calling_sequence +\
                                'EOF\n'
        os.system(self.calling_sequence)
        self.old_calling_sequence.append(self.calling_sequence)
        self.calling_sequence = ''
        os.chdir(self.mycwd)
        return