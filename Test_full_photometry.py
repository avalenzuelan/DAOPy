#!/usr/bin/env python3

# Runs all modules to create ALLFRAME new photometry for NPL058 field, in all 4 
# chips.

from modules import OPTFiles, FitsImage, DaophotExecution, DaomasterExecution,\
                    DaomatchExecution, AllstarExecution, AllframeExecution

def pause():
    programPause = input("Press the <ENTER> key to continue...")

path_to_chip='../Data/NPL058/c1/maxsig-0.5_minframes_2'

print('Hello! Welcome to the Python wrapper for DAOPHOT')
print('Photometry for NPL058 field, chip 1')

###############################################################################
# --------- PART 1: GETTING THE PSF STARS ------------------------------------
###############################################################################

filename_npl058_Ks_long = 'NPL058_Ks_160s_c1.fits'
filename_npl058_H_long = 'NPL058_H_480s_c1.fits'

npl058_Ks_long = FitsImage(path_to_folder=path_to_chip,
                           fits_filename=filename_npl058_Ks_long,
                           field_name='NPL058',
                           texp=160,
                           filter='Ks')

npl058_H_long = FitsImage(path_to_folder=path_to_chip,
                           fits_filename=filename_npl058_H_long,
                           field_name='NPL058',
                           texp=480,
                           filter='H')

print('--- Creating long opt files ...')

opt_files_long = OPTFiles(path_to_folder = path_to_chip,
                     filename = 'opt_files_long_exps.json')

opt_files_long.params = 'daophot', 'th', 1 #Change the threshold
opt_files_long.params = 'daophot', 'ga', 1.7 #From manual
opt_files_long.params = 'daophot', 're', npl058_H_long.ron

opt_files_long.create_opt_files(path_to_opts=path_to_chip)
print('Done!')

# ------------------------------ Long phot -------------------------------------
print('Executing DAOPHOT for %s ...' %npl058_Ks_long.filename)

daophot_Ks_long = DaophotExecution(path_to_folder=path_to_chip,
                                   filename=npl058_Ks_long.filename,
                                   summed=8,
                                   averaged=2)
daophot_Ks_long.attach_image(daophot_Ks_long.filename)
daophot_Ks_long.find_stars()
daophot_Ks_long.aperture_phot()
daophot_Ks_long.pick_stars(200,15)
daophot_Ks_long.execute()
print('Done!')

print('Executing DAOPHOT for %s ...' %npl058_H_long.filename)

daophot_H_long = DaophotExecution(path_to_folder=path_to_chip,
                                   filename=npl058_H_long.filename,
                                   summed=16,
                                   averaged=3)
daophot_H_long.attach_image(daophot_H_long.filename)
daophot_H_long.find_stars()
daophot_H_long.aperture_phot()
daophot_H_long.pick_stars(200,15)
daophot_H_long.execute()
print('Done!')


#------------------------------ Short Phot -------------------------------------
#changing the opt files for short exposures

filename_npl058_H_short = 'NPL058_H_10s_c1.fits'
filename_npl058_Ks_short = 'NPL058_Ks_10s_c1.fits'

npl058_Ks_short = FitsImage(path_to_folder=path_to_chip,
                           fits_filename=filename_npl058_Ks_short,
                           field_name='NPL058',
                           texp=10,
                           filter='Ks')

npl058_H_short = FitsImage(path_to_folder=path_to_chip,
                           fits_filename=filename_npl058_H_short,
                           field_name='NPL058',
                           texp=10,
                           filter='H')

print('--- Creating short opt files ...')

opt_files_short = OPTFiles(path_to_folder = path_to_chip,
                     filename = 'opt_files_short_exps.json')
opt_files_short.params = 'daophot', 'th', 1
opt_files_short.params = 'daophot', 'ga', 1.7 #From manual
opt_files_short.params = 'daophot', 're', npl058_Ks_short.ron
opt_files_short.create_opt_files(path_to_opts=path_to_chip)

print('Executing DAOPHOT for %s ...' %npl058_Ks_short.filename)

daophot_Ks_short = DaophotExecution(path_to_folder=path_to_chip,
                                   filename=npl058_Ks_short.filename,
                                   summed=5,
                                   averaged=1,
                                   niter_psf=2)
daophot_Ks_short.attach_image(daophot_Ks_short.filename)
daophot_Ks_short.find_stars()
daophot_Ks_short.aperture_phot()
daophot_Ks_short.pick_stars(200,15)
daophot_Ks_short.execute()
print('Done!')

print('Executing DAOPHOT for %s ...' %npl058_H_short.filename)

daophot_H_short = DaophotExecution(path_to_folder=path_to_chip,
                                   filename=npl058_H_short.filename,
                                   summed=5,
                                   averaged=1,
                                   niter_psf=3)
daophot_H_short.attach_image(daophot_H_short.filename)
daophot_H_short.find_stars()
daophot_H_short.aperture_phot()
daophot_H_short.pick_stars(200,15)
daophot_H_short.execute()
print('Done!')

#------------------------------ .lst selection ---------------------------------
#Here you have to edit the .lst file and select suitable psf stars. You can do
#it with the software of your preference. Here I leave a script called
#"select_psf_stars_lst.py" that does that. You can use it or not, it's up to you

#Pause the program until you are done editing the .lst file
print('Please edit the .lst file and select suitable psf stars ...')
pause()

###############################################################################
# --------- PART 2: MAKING THE PSF MODEL  --------------------------------------
###############################################################################

# ------------------------------ Long phot -------------------------------------

print('--- Creating long opt files ...')

opt_files_long = OPTFiles(path_to_folder = path_to_chip,
                     filename = 'opt_files_long_exps.json')

opt_files_long.params = 'daophot', 'th', 5 #Change the threshold
opt_files_long.params = 'daophot', 'ga', 1.7 #From manual
opt_files_long.params = 'daophot', 're', npl058_H_long.ron

opt_files_long.create_opt_files(path_to_opts=path_to_chip)

# Ks long
daophot_Ks_long.attach_image(daophot_Ks_long.filename)
daophot_Ks_long.psf_model()
daophot_Ks_long.substar()
daophot_Ks_long.execute()

#making 2nd psf model
daophot_Ks_long.attach_image(daophot_Ks_long.filename + 's')
daophot_Ks_long.psf_model(delete=False,
                        ap_name=daophot_Ks_long.filename + '.ap',
                        psf_name=daophot_Ks_long.filename + 's.psf',
                        nei_name=daophot_Ks_long.filename + 's.nei')
daophot_Ks_long.execute()
print('Done!')

#H long
daophot_H_long.attach_image(daophot_H_long.filename)
daophot_H_long.psf_model()
daophot_H_long.substar()
daophot_H_long.execute()

#making 2nd psf model
daophot_H_long.attach_image(daophot_H_long.filename + 's')
daophot_H_long.psf_model(delete=False,
                        ap_name=daophot_H_long.filename + '.ap',
                        psf_name=daophot_H_long.filename + 's.psf',
                        nei_name=daophot_H_long.filename + 's.nei')
daophot_H_long.execute()
print('Done!')

# ------------------------------ Short phot ------------------------------------

print('--- Creating short opt files ...')

opt_files_short = OPTFiles(path_to_folder = path_to_chip,
                     filename = 'opt_files_short_exps.json')
opt_files_short.params = 'daophot', 'th', 5
opt_files_short.params = 'daophot', 'ga', 1.7 #From manual
opt_files_short.params = 'daophot', 're', npl058_Ks_short.ron
opt_files_short.create_opt_files(path_to_opts=path_to_chip)

# Ks short
daophot_Ks_short.attach_image(daophot_Ks_short.filename)
daophot_Ks_short.psf_model()
daophot_Ks_short.substar()
daophot_Ks_short.execute()

#making 2nd psf model
daophot_Ks_short.attach_image(daophot_Ks_short.filename + 's')
daophot_Ks_short.psf_model(delete=False,
                        ap_name=daophot_Ks_short.filename + '.ap',
                        psf_name=daophot_Ks_short.filename + 's.psf',
                        nei_name=daophot_Ks_short.filename + 's.nei')
daophot_Ks_short.execute()
print('Done!')

#H short
daophot_H_short.attach_image(daophot_H_short.filename)
daophot_H_short.psf_model()
daophot_H_short.substar()
daophot_H_short.execute()

#making 2nd psf model
daophot_H_short.attach_image(daophot_H_short.filename + 's')
daophot_H_short.psf_model(delete=False,
                        ap_name=daophot_H_short.filename + '.ap',
                        psf_name=daophot_H_short.filename + 's.psf',
                        nei_name=daophot_H_short.filename + 's.nei')
daophot_H_short.execute()
print('Done!')

###############################################################################
# --------- PART 3: RUNNING ALLSTAR  ------------------------------------------
###############################################################################

# ------------------------------ Long phot -------------------------------------

allstar_Ks_long = AllstarExecution(path_to_folder=path_to_chip,
                                      filename=npl058_Ks_long.filename,)

allstar_Ks_long.allstar(psf_name=daophot_Ks_long.filename + 's.psf',
                        ap_name=daophot_Ks_long.filename + '.ap',
                        als_name=daophot_Ks_long.filename + '.als',
                        sub_fits_name=daophot_Ks_long.filename + 'ss.fits')
allstar_Ks_long.execute()

allstar_H_long = AllstarExecution(path_to_folder=path_to_chip,
                                      filename=npl058_H_long.filename,)

allstar_H_long.allstar(psf_name=daophot_H_long.filename + 's.psf',
                        ap_name=daophot_H_long.filename + '.ap',
                        als_name=daophot_H_long.filename + '.als',
                        sub_fits_name=daophot_H_long.filename + 'ss.fits')
allstar_H_long.execute()

# ------------------------------ Short phot ------------------------------------

allstar_Ks_short = AllstarExecution(path_to_folder=path_to_chip,
                                      filename=npl058_Ks_short.filename,)

allstar_Ks_short.allstar(psf_name=daophot_Ks_short.filename + 's.psf',
                        ap_name=daophot_Ks_short.filename + '.ap',
                        als_name=daophot_Ks_short.filename + '.als',
                        sub_fits_name=daophot_Ks_short.filename + 'ss.fits')
allstar_Ks_short.execute()

allstar_H_short = AllstarExecution(path_to_folder=path_to_chip,
                                      filename=npl058_H_short.filename,)

allstar_H_short.allstar(psf_name=daophot_H_short.filename + 's.psf',
                        ap_name=daophot_H_short.filename + '.ap',
                        als_name=daophot_H_short.filename + '.als',
                        sub_fits_name=daophot_H_short.filename + 'ss.fits')
allstar_H_short.execute()

###############################################################################
# --------- PART 4: RUNNING ALLFRAME ------------------------------------------
###############################################################################

# ------------------------------ DAOMATCH -------------------------------------
print('Executing DAOMATCH')

daomatch_npl058_c1 = DaomatchExecution(path_to_folder=path_to_chip,
                                     master_filename=npl058_Ks_long.filename,
                                     list_of_filenames=[
                                            npl058_H_long.filename,
                                            npl058_Ks_short.filename,
                                            npl058_H_short.filename,
                                     ])
daomatch_npl058_c1.daomatch(mch_name='NPL058_c1')
daomatch_npl058_c1.execute()
print('Done!')

# ------------------------------ DAOMASTER -------------------------------------

print('Executing DAOMASTER')

daomaster_npl058_c1 = DaomasterExecution(path_to_folder=path_to_chip,
                                         mch_filename='NPL058_c1',
                                         n_files=4)

daomaster_npl058_c1.daomaster()
daomaster_npl058_c1.execute()


# ------------------------------ ALLFRAME -------------------------------------

print('Executing ALLFRAME')

allframe_npl058_c1 = AllframeExecution(path_to_folder=path_to_chip,
                                        mch_filename='NPL058_c1',
                                        mag_filename='NPL058_c1',
                                        )
allframe_npl058_c1.allframe()
allframe_npl058_c1.execute()
print('Done!')

###############################################################################
# -------------------------------- ALL DONE -----------------------------------
###############################################################################