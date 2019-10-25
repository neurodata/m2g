# import os
# import pytest
# import pkg_resources
# import glob
# import random
# import shutil
# from pathlib2 import Path
# from ndmg.scripts import ndmg_dwi_pipeline
# from itertools import product
# from ndmg.utils.bids_utils import name_resource

# # atlases = ['desikan', 'CPAC200', 'DKT', 'HarvardOxfordcort', 'HarvardOxfordsub', 'JHU', 'Schaefer2018-200', 'Talairach', 'aal', 'brodmann', 'glasser', 'yeo-7-liberal', 'yeo-17-liberal']
# # mod_types = ['det', 'prob']
# # track_types = ['local', 'particle']
# # mods = ['csa', 'csd']
# # regs = ['native', 'native_dsn', 'mni']
# # grid = list(product(atlases, mod_types, track_types, mods, regs))

# for f in glob.glob("/tmp/output*"):
#     os.remove(f)


# def is_graph(filename, atlas="", suffix=""):
#     """
#     Check if `filename` is a ndmg graph file.

#     Parameters
#     ----------
#     filename : str or Path
#         location of the file.

#     Returns
#     -------
#     bool
#         True if the file has the ndmg naming convention, else False.
#     """

#     if atlas:
#         atlas = atlas.lower()
#         KEYWORDS.append(atlas)

#     if suffix:
#         if not suffix.startswith("."):
#             suffix = "." + suffix

#     correct_suffix = Path(filename).suffix == suffix
#     correct_filename = all(i in str(filename) for i in KEYWORDS)
#     return correct_suffix and correct_filename


# def filter_graph_files(file_list, **kwargs):
#     """
#     Generator.
#     Check if each file in `file_list` is a ndmg edgelist,
#     yield it if it is.

#     Parameters
#     ----------
#     file_list : iterator
#         iterator of inputs to the `is_graph` function.
#     """
#     for filename in file_list:
#         if is_graph(filename, **kwargs):
#             yield (filename)


# def get_files(output_directory, suffix="ssv", atlas="desikan"):
#     output = []
#     for dirname, _, files in os.walk(output_directory):
#         file_ends = list(filter_graph_files(files, suffix=suffix, atlas=atlas))
#         graphnames = [Path(dirname) / Path(graphname) for graphname in file_ends]
#         if all(graphname.exists for graphname in graphnames):
#             output.extend(graphnames)
#     return output


# @pytest.mark.parametrize("atlas,mod_type,track_type,mod_func,reg_style", grid)
# def test_fuzz_dwi_pipeline(atlas, mod_type, track_type, mod_func, reg_style):
#     base_dir = str(Path(__file__).parent.parent / "data")
#     home = str(Path.home())
#     dir_path = base_dir + "/BNU1"
#     outdir = "/tmp/output_{}_{}_{}_{}_{}".format(
#         atlas, mod_type, track_type, mod_func, reg_style
#     )
#     vox_size = "2mm"
#     clean = False
#     skipeddy = True
#     t1w = dir_path + "/sub-0025864/ses-1/anat/sub-0025864_ses-1_T1w.nii.gz"
#     bvals = dir_path + "/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.bval"
#     bvecs = dir_path + "/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.bvec"
#     dwi = dir_path + "/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.nii.gz"
#     mask = (
#         home
#         + "/.ndmg/ndmg_atlases/atlases/mask/MNI152NLin6_res-2x2x2_T1w_descr-brainmask.nii.gz"
#     )
#     labels = [
#         i
#         for i in glob.glob(
#             home + "/.ndmg/ndmg_atlases/atlases/label/Human/*2x2x2.nii.gz"
#         )
#         if atlas in i
#     ]

#     # Create directory tree
#     namer = name_resource(dwi, t1w, atlas, outdir)

#     print("Output directory: " + outdir)
#     if not os.path.isdir(outdir):
#         cmd = "mkdir -p {}".format(outdir)
#         os.system(cmd)
#     paths = {
#         "prep_dwi": "dwi/preproc",
#         "prep_anat": "anat/preproc",
#         "reg_anat": "anat/registered",
#         "fiber": "dwi/fiber",
#         "conn": "dwi/roi-connectomes",
#     }
#     label_dirs = ["conn"]  # create label level granularity
#     print("Adding directory tree...")
#     namer.add_dirs_dwi(paths, labels, label_dirs)

#     dwi_prep = "{}/eddy_corrected_data.nii.gz".format(namer.dirs["output"]["prep_dwi"])
#     shutil.copyfile(
#         dir_path + "/sub-0025864/ses-1/dwi/eddy_corrected_data.nii.gz", dwi_prep
#     )

#     # Run pipeline
#     ndmg_dwi_pipeline.ndmg_dwi_worker(
#         dwi,
#         bvals,
#         bvecs,
#         t1w,
#         atlas,
#         mask,
#         labels,
#         outdir,
#         vox_size,
#         mod_type,
#         track_type,
#         mod_func,
#         reg_style,
#         clean,
#         skipeddy,
#     )
#     output = get_files(outdir)
#     assert output is not None
