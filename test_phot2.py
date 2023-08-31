#!/usr/bin/env python3

# This script is to test the photometry routines after the selection of the
# PSF stars.

from modules import OPTFiles, FitsImage, DaophotExecution

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
# ------------------------------ Long phot -------------------------------------
print('Executing DAOPHOT for %s ...' %npl054_Ks_long.filename)

daophot_Ks_long = DaophotExecution(path_to_folder=path_to_chip,
                                   filename=npl054_Ks_long.filename,
                                   summed=8,
                                   averaged=2,
                                   niter_psf=2)
daophot_Ks_long.attach_image(daophot_Ks_long.filename)
daophot_Ks_long.psf_model()
daophot_Ks_long.substar() #For now, I'll skip this step and go straight to ALLSTAR
daophot_Ks_long.execute()

#making 2nd psf model
daophot_Ks_long.attach_image(daophot_Ks_long.filename + 's')
daophot_Ks_long.psf_model(delete=False,
                        ap_name=daophot_Ks_long.filename + '.ap',
                        psf_name=daophot_Ks_long.filename + 's.psf',
                        nei_name=daophot_Ks_long.filename + 's.nei')
daophot_Ks_long.execute()
print('Done!')

print('Executing DAOPHOT for %s ...' %npl054_H_long.filename)

daophot_H_long = DaophotExecution(path_to_folder=path_to_chip,
                                   filename=npl054_H_long.filename,
                                   summed=16,
                                   averaged=3,
                                   niter_psf=3)

print('Done!')


#------------------------------ Short Phot -------------------------------------
#changing the opt files for short exposures
# opt_files_short = OPTFiles(path_to_folder = path_to_chip,
#                      filename = 'opt_files_short_exps.json')
# opt_files_short.params = 'daophot', 'th', 1
# opt_files_short.create_opt_files(path_to_opts=path_to_chip)

print('Executing DAOPHOT for %s ...' %npl054_Ks_short.filename)

daophot_Ks_short = DaophotExecution(path_to_folder=path_to_chip,
                                   filename=npl054_Ks_short.filename,
                                   summed=5,
                                   averaged=1,
                                   niter_psf=2)

print('Done!')

print('Executing DAOPHOT for %s ...' %npl054_H_short.filename)

daophot_H_short = DaophotExecution(path_to_folder=path_to_chip,
                                   filename=npl054_H_short.filename,
                                   summed=5,
                                   averaged=1,
                                   niter_psf=3)

print('Done!')

