#!/usr/bin/env python3

# This script is to run DAOMATCH, DAOMASTER and ALLFRAME

from modules import OPTFiles, FitsImage, \
    DaophotExecution, AllstarExecution, DaomatchExecution, \
    DaomasterExecution, AllframeExecution

path_to_chip='../Data/NPL054/c1'

print('Hello! Welcome to the Python wrapper for DAOPHOT')
print('Photometry for NPL054 field, chip 1')

opt_files_long = OPTFiles(path_to_folder = path_to_chip,
                     filename = 'opt_files_long_exps.json')
print('--- Creating long opt files ...')

opt_files_long.params = 'daophot', 'th', 1 #Change the threshold to detect only "good" stars
opt_files_long.create_opt_files(path_to_opts=path_to_chip)
print('Done!')
print('--- Opening .fits files ...')

filename_npl054_Ks_long = 'NPL054_Ks_160s_c1.fits'
filename_npl054_Ks_short = 'NPL054_Ks_10s_c1.fits'

filename_npl054_H_long = 'NPL054_H_480s_c1.fits'
filename_npl054_H_short = 'NPL054_H_10s_c1.fits'

npl054_Ks_long = FitsImage(path_to_folder=path_to_chip,
                           fits_filename=filename_npl054_Ks_long,
                           field_name='NPL054',
                           texp=160,
                           filter='Ks')

npl054_H_long = FitsImage(path_to_folder=path_to_chip,
                           fits_filename=filename_npl054_H_long,
                           field_name='NPL054',
                           texp=480,
                           filter='H')

npl054_Ks_short = FitsImage(path_to_folder=path_to_chip,
                           fits_filename=filename_npl054_Ks_short,
                           field_name='NPL054',
                           texp=10,
                           filter='Ks')

npl054_H_short = FitsImage(path_to_folder=path_to_chip,
                           fits_filename=filename_npl054_H_short,
                           field_name='NPL054',
                           texp=10,
                           filter='H')

print('Done!')
# ------------------------------ DAOMATCH -------------------------------------
print('Executing DAOMATCH')

daomatch_npl054_c1 = DaomatchExecution(path_to_folder=path_to_chip,
                                     master_filename=npl054_Ks_long.filename,
                                     list_of_filenames=[
                                            npl054_H_long.filename,
                                            npl054_Ks_short.filename,
                                            npl054_H_short.filename,
                                     ])
daomatch_npl054_c1.daomatch(mch_name='NPL054_c1')
daomatch_npl054_c1.execute()
print('Done!')

# ------------------------------ DAOMASTER -------------------------------------

print('Executing DAOMASTER')

daomaster_npl054_c1 = DaomasterExecution(path_to_folder=path_to_chip,
                                         mch_filename='NPL054_c1',
                                         n_files=4)

daomaster_npl054_c1.daomaster()
daomaster_npl054_c1.execute()


# ------------------------------ ALLFRAME -------------------------------------

print('Executing ALLFRAME')

allframe_npl054_c1 = AllframeExecution(path_to_folder=path_to_chip,
                                        mch_filename='NPL054_c1',
                                        mag_filename='NPL054_c1',
                                        )
allframe_npl054_c1.allframe()
allframe_npl054_c1.execute()
print('Done!')

#THE END
                                       