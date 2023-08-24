from modules import OPTFiles, FitsImage, DaophotExecution

path_to_chip='/../Artificial_Stars_experiments/Data/NPL058/c4'

print('Hello! Welcome to the Python wrapper for DAOPHOT')
print('Long Exposure photometry for NPL058 field, chip 4')

opt_files = OPTFiles('opt_files_long_exps.json')
print('--- Creating long opt files ...')

opt_files.params = 'daophot', 'th', 5 #Change the threshold to detect only "good" stars
opt_files.create_opt_files(path_to_opts=path_to_chip)
print('Done!')
print('--- Opening .fits files ...')

filename_npl058_Ks_long = 'NPL058_Ks_160s_c4.fits'
filename_npl058_Ks_short = 'NPL058_Ks_10s_c4.fits'

filename_npl058_H_long = 'NPL058_H_480s_c4.fits'
filename_npl058_H_short = 'NPL058_Ks_10s_c4.fits'

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

print('Done!')
print('Executing DAOPHOT for %s ...' %npl058_Ks_long.filename)

daophot_Ks_long = DaophotExecution(path_to_folder=path_to_chip,
                                   filename=npl058_Ks_long.filename,
                                   summed=8,
                                   averaged=2,
                                   niter_psf=2)
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
                                   averaged=3,
                                   niter_psf=3)
daophot_H_long.attach_image(daophot_H_long.filename)
daophot_H_long.find_stars()
daophot_H_long.aperture_phot()
daophot_H_long.pick_stars(200,15)
daophot_H_long.execute()
print('Done!')

#Here you have to edit the .lst file and select suitable psf stars. You can do
#it with the software of your preference. Here I leave a script called
#"select_psf_stars_lst.py" that does that. You can use it or not, it's up to you

print('Executing model PSF for %s ...' %npl058_Ks_long.filename)
daophot_Ks_long.attach_image(daophot_Ks_long.filename)
daophot_Ks_long.psf_model()
daophot_Ks_long.substar()
daophot_Ks_long.execute()
print('Done!')