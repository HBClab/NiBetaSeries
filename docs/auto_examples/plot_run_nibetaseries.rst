.. note::
    :class: sphx-glr-download-link-note

    Click :ref:`here <sphx_glr_download_auto_examples_plot_run_nibetaseries.py>` to download the full example code
.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_examples_plot_run_nibetaseries.py:


Running NiBetaSeries using ds000164 (Stroop Task)
===============================================================

This example runs through a basic call of NiBetaSeries using
the commandline entry point ``nibs``.
While this example is using python, typically ``nibs`` will be
called directly on the commandline.

Import all the necessary packages
=================================


.. code-block:: default


    import tempfile  # make a temporary directory for files
    import os  # interact with the filesystem
    import urllib.request  # grad data from internet
    import tarfile  # extract files from tar
    from subprocess import Popen, PIPE, STDOUT  # enable calling commandline

    import matplotlib.pyplot as plt  # manipulate figures
    import seaborn as sns  # display results
    import pandas as pd   # manipulate tabular data







Download relevant data from ds000164 (and Atlas Files)
======================================================
The subject data came from `openneuro <https://openneuro.org/datasets/ds000164/versions/00001/>`_.
The atlas data came from a `recently published parcellation <https://www.ncbi.nlm.nih.gov/pubmed/28981612>`_
in a publically accessible github repository.


.. code-block:: default


    # atlas github repo for reference:
    """https://github.com/ThomasYeoLab/CBIG/raw/master/stable_projects/\
    brain_parcellation/Schaefer2018_LocalGlobal/Parcellations/MNI/"""
    data_dir = tempfile.mkdtemp()
    print('Our working directory: {}'.format(data_dir))

    # download the tar data
    url = "https://www.dropbox.com/s/qoqbiya1ou7vi78/ds000164-test_v1.tar.gz?dl=1"
    tar_file = os.path.join(data_dir, "ds000164.tar.gz")
    u = urllib.request.urlopen(url)
    data = u.read()
    u.close()

    # write tar data to file
    with open(tar_file, "wb") as f:
        f.write(data)

    # extract the data
    tar = tarfile.open(tar_file, mode='r|gz')
    tar.extractall(path=data_dir)

    os.remove(tar_file)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Our working directory: /var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a


Display the minimal dataset necessary to run nibs
=================================================


.. code-block:: default



    # https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
    def list_files(startpath):
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * (level)
            print('{}{}/'.format(indent, os.path.basename(root)))
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                print('{}{}'.format(subindent, f))


    list_files(data_dir)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    tmppvvwl83a/
        ds000164/
            CHANGES
            dataset_description.json
            README
            T1w.json
            task-stroop_bold.json
            task-stroop_events.json
            derivatives/
                data/
                    Schaefer2018_100Parcels_7Networks_order.txt
                    Schaefer2018_100Parcels_7Networks_order_FSLMNI152_2mm.nii.gz
                fmriprep/
                    sub-001/
                        func/
                            sub-001_task-stroop_bold_confounds.tsv
                            sub-001_task-stroop_bold_space-MNI152NLin2009cAsym_brainmask.nii.gz
                            sub-001_task-stroop_bold_space-MNI152NLin2009cAsym_preproc.nii.gz
            sub-001/
                anat/
                    sub-001_T1w.nii.gz
                func/
                    sub-001_task-stroop_bold.nii.gz
                    sub-001_task-stroop_events.tsv


Manipulate events file so it satifies assumptions
=================================================
1. the correct column has 1's and 0's corresponding to correct and incorrect,
respectively.
2. the condition column is renamed to trial_type
nibs currently depends on the "correct" column being binary
and the "trial_type" column to contain the trial types of interest.

read the file
-------------


.. code-block:: default


    events_file = os.path.join(data_dir,
                               "ds000164",
                               "sub-001",
                               "func",
                               "sub-001_task-stroop_events.tsv")
    events_df = pd.read_csv(events_file, sep='\t', na_values="n/a")
    print(events_df.head())





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    onset  duration correct  condition  response_time
    0   0.342         1       Y    neutral          1.186
    1   3.345         1       Y  congruent          0.667
    2  12.346         1       Y  congruent          0.614
    3  15.349         1       Y    neutral          0.696
    4  18.350         1       Y    neutral          0.752


change the Y/N to 1/0
---------------------


.. code-block:: default


    events_df['correct'].replace({"Y": 1, "N": 0}, inplace=True)
    print(events_df.head())





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    onset  duration  correct  condition  response_time
    0   0.342         1        1    neutral          1.186
    1   3.345         1        1  congruent          0.667
    2  12.346         1        1  congruent          0.614
    3  15.349         1        1    neutral          0.696
    4  18.350         1        1    neutral          0.752


replace condition with trial_type
---------------------------------


.. code-block:: default


    events_df.rename({"condition": "trial_type"}, axis='columns', inplace=True)
    print(events_df.head())





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    onset  duration  correct trial_type  response_time
    0   0.342         1        1    neutral          1.186
    1   3.345         1        1  congruent          0.667
    2  12.346         1        1  congruent          0.614
    3  15.349         1        1    neutral          0.696
    4  18.350         1        1    neutral          0.752


save the file
-------------


.. code-block:: default


    events_df.to_csv(events_file, sep="\t", na_rep="n/a", index=False)







Manipulate the region order file
================================
There are several adjustments to the atlas file that need to be completed
before we can pass it into nibs.
Importantly, the relevant column names **MUST** be named "index" and "regions".
"index" refers to which integer within the file corresponds to which region
in the atlas nifti file.
"regions" refers the name of each region in the atlas nifti file.

read the atlas file
-------------------


.. code-block:: default


    atlas_txt = os.path.join(data_dir,
                             "ds000164",
                             "derivatives",
                             "data",
                             "Schaefer2018_100Parcels_7Networks_order.txt")
    atlas_df = pd.read_csv(atlas_txt, sep="\t", header=None)
    print(atlas_df.head())





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    0                   1    2   3    4  5
    0  1  7Networks_LH_Vis_1  120  18  131  0
    1  2  7Networks_LH_Vis_2  120  18  132  0
    2  3  7Networks_LH_Vis_3  120  18  133  0
    3  4  7Networks_LH_Vis_4  120  18  135  0
    4  5  7Networks_LH_Vis_5  120  18  136  0


drop coordinate columns
-----------------------


.. code-block:: default


    atlas_df.drop([2, 3, 4, 5], axis='columns', inplace=True)
    print(atlas_df.head())





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    0                   1
    0  1  7Networks_LH_Vis_1
    1  2  7Networks_LH_Vis_2
    2  3  7Networks_LH_Vis_3
    3  4  7Networks_LH_Vis_4
    4  5  7Networks_LH_Vis_5


rename columns with the approved headings: "index" and "regions"
----------------------------------------------------------------


.. code-block:: default


    atlas_df.rename({0: 'index', 1: 'regions'}, axis='columns', inplace=True)
    print(atlas_df.head())





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    index             regions
    0      1  7Networks_LH_Vis_1
    1      2  7Networks_LH_Vis_2
    2      3  7Networks_LH_Vis_3
    3      4  7Networks_LH_Vis_4
    4      5  7Networks_LH_Vis_5


remove prefix "7Networks"
-------------------------


.. code-block:: default


    atlas_df.replace(regex={'7Networks_(.*)': '\\1'}, inplace=True)
    print(atlas_df.head())





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    index   regions
    0      1  LH_Vis_1
    1      2  LH_Vis_2
    2      3  LH_Vis_3
    3      4  LH_Vis_4
    4      5  LH_Vis_5


write out the file as .tsv
--------------------------


.. code-block:: default


    atlas_tsv = atlas_txt.replace(".txt", ".tsv")
    atlas_df.to_csv(atlas_tsv, sep="\t", index=False)







Run nibs
========


.. code-block:: default

    out_dir = os.path.join(data_dir, "ds000164", "derivatives")
    work_dir = os.path.join(out_dir, "work")
    atlas_mni_file = os.path.join(data_dir,
                                  "ds000164",
                                  "derivatives",
                                  "data",
                                  "Schaefer2018_100Parcels_7Networks_order_FSLMNI152_2mm.nii.gz")
    cmd = """\
    nibs -c WhiteMatter CSF \
    --participant_label 001 \
    -w {work_dir} \
    -a {atlas_mni_file} \
    -l {atlas_tsv} \
    {bids_dir} \
    fmriprep \
    {out_dir} \
    participant
    """.format(atlas_mni_file=atlas_mni_file,
               atlas_tsv=atlas_tsv,
               bids_dir=os.path.join(data_dir, "ds000164"),
               out_dir=out_dir,
               work_dir=work_dir)
    # call nibs
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)

    while True:
        line = p.stdout.readline()
        if not line:
            break
        print(line)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    b"/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/site-packages/grabbit/core.py:449: UserWarning: Domain with name 'bids' already exists; returning existing Domain configuration.\n"
    b'  warnings.warn(msg)\n'
    b'/Users/peerherholz/anaconda2/envs/py36/lib/python3.6/subprocess.py:766: ResourceWarning: subprocess 17858 is still running\n'
    b'  ResourceWarning, source=self)\n'
    b"/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/site-packages/nipype/utils/profiler.py:181: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='UTF-8'>\n"
    b"  mem_str = os.popen('sysctl hw.memsize').read().strip().split(' ')[-1]\n"
    b'190415-14:38:15,970 nipype.workflow INFO:\n'
    b"\t Workflow nibetaseries_participant_wf settings: ['check', 'execution', 'logging', 'monitoring']\n"
    b'190415-14:38:16,37 nipype.workflow INFO:\n'
    b'\t Running in parallel.\n'
    b'190415-14:38:16,64 nipype.workflow INFO:\n'
    b'\t [MultiProc] Running 0 tasks, and 1 jobs ready. Free memory (GB): 10.80/10.80, Free processors: 4/4.\n'
    b'190415-14:38:16,153 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "nibetaseries_participant_wf.single_subject001_wf.betaseries_wf.betaseries_node" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/betaseries_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/betaseries_node".\n'
    b'190415-14:38:16,161 nipype.workflow INFO:\n'
    b'\t [Node] Running "betaseries_node" ("nibetaseries.interfaces.nistats.BetaSeries")\n'
    b"/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/importlib/_bootstrap.py:219: ImportWarning: can't resolve package from __spec__ or __package__, falling back on __name__ and __path__\n"
    b'  return f(*args, **kwds)\n'
    b'/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/site-packages/nibabel/nifti1.py:582: DeprecationWarning: The binary mode of fromstring is deprecated, as it behaves surprisingly on unicode inputs. Use frombuffer instead\n'
    b'  ext_def = np.fromstring(ext_def, dtype=np.int32)\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b"/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/site-packages/nistats/hemodynamic_models.py:268: DeprecationWarning: object of type <class 'numpy.float64'> cannot be safely interpreted as an integer.\n"
    b'  frame_times.max() * (1 + 1. / (n - 1)), n_hr)\n'
    b"/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/site-packages/nistats/hemodynamic_models.py:55: DeprecationWarning: object of type <class 'float'> cannot be safely interpreted as an integer.\n"
    b'  time_stamps = np.linspace(0, time_length, float(time_length) / dt)\n'
    b'\n'
    b'Computation of 1 runs done in 1 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'190415-14:38:18,57 nipype.workflow INFO:\n'
    b'\t [MultiProc] Running 1 tasks, and 0 jobs ready. Free memory (GB): 10.60/10.80, Free processors: 3/4.\n'
    b'                     Currently running:\n'
    b'                       * nibetaseries_participant_wf.single_subject001_wf.betaseries_wf.betaseries_node\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 1 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 1 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 1 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 1 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 1 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 1 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 1 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 1 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 1 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 1 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 1 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 1 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 1 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'Computing run 1 out of 1 runs (go take a coffee, a big one)\n'
    b'\n'
    b'Computation of 1 runs done in 0 seconds\n'
    b'\n'
    b'/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/site-packages/nipype/pipeline/engine/utils.py:307: DeprecationWarning: use "HasTraits.trait_set" instead\n'
    b'  result.outputs.set(**modify_paths(tosave, relative=True, basedir=cwd))\n'
    b'190415-14:40:16,476 nipype.workflow INFO:\n'
    b'\t [Node] Finished "nibetaseries_participant_wf.single_subject001_wf.betaseries_wf.betaseries_node".\n'
    b'190415-14:40:18,151 nipype.workflow INFO:\n'
    b'\t [Job 0] Completed (nibetaseries_participant_wf.single_subject001_wf.betaseries_wf.betaseries_node).\n'
    b'190415-14:40:18,286 nipype.workflow INFO:\n'
    b'\t [MultiProc] Running 0 tasks, and 1 jobs ready. Free memory (GB): 10.80/10.80, Free processors: 4/4.\n'
    b'190415-14:40:20,187 nipype.workflow INFO:\n'
    b'\t [MultiProc] Running 0 tasks, and 3 jobs ready. Free memory (GB): 10.80/10.80, Free processors: 4/4.\n'
    b'190415-14:40:20,227 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_atlas_corr_node0" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/correlation_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/atlas_corr_node/mapflow/_atlas_corr_node0".\n'
    b'190415-14:40:20,229 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_atlas_corr_node1" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/correlation_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/atlas_corr_node/mapflow/_atlas_corr_node1".\n'
    b'190415-14:40:20,232 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_atlas_corr_node2" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/correlation_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/atlas_corr_node/mapflow/_atlas_corr_node2".\n'
    b'190415-14:40:20,234 nipype.workflow INFO:\n'
    b'\t [Node] Running "_atlas_corr_node0" ("nibetaseries.interfaces.nilearn.AtlasConnectivity")\n'
    b'190415-14:40:20,237 nipype.workflow INFO:\n'
    b'\t [Node] Running "_atlas_corr_node1" ("nibetaseries.interfaces.nilearn.AtlasConnectivity")\n'
    b'190415-14:40:20,239 nipype.workflow INFO:\n'
    b'\t [Node] Running "_atlas_corr_node2" ("nibetaseries.interfaces.nilearn.AtlasConnectivity")\n'
    b"/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/importlib/_bootstrap.py:219: ImportWarning: can't resolve package from __spec__ or __package__, falling back on __name__ and __path__\n"
    b'  return f(*args, **kwds)\n'
    b"/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/importlib/_bootstrap.py:219: ImportWarning: can't resolve package from __spec__ or __package__, falling back on __name__ and __path__\n"
    b'  return f(*args, **kwds)\n'
    b"/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/importlib/_bootstrap.py:219: ImportWarning: can't resolve package from __spec__ or __package__, falling back on __name__ and __path__\n"
    b'  return f(*args, **kwds)\n'
    b"/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/importlib/_bootstrap.py:219: ImportWarning: can't resolve package from __spec__ or __package__, falling back on __name__ and __path__\n"
    b'  return f(*args, **kwds)\n'
    b"/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/importlib/_bootstrap.py:219: ImportWarning: can't resolve package from __spec__ or __package__, falling back on __name__ and __path__\n"
    b'  return f(*args, **kwds)\n'
    b"/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/importlib/_bootstrap.py:219: ImportWarning: can't resolve package from __spec__ or __package__, falling back on __name__ and __path__\n"
    b'  return f(*args, **kwds)\n'
    b'[NiftiLabelsMasker.fit_transform] loading data from /var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/data/Schaefer2018_100Parcels_7Networks_order_FSLMNI152_2mm.nii.gz\n'
    b'[NiftiLabelsMasker.fit_transform] loading data from /var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/data/Schaefer2018_100Parcels_7Networks_order_FSLMNI152_2mm.nii.gz\n'
    b'[NiftiLabelsMasker.fit_transform] loading data from /var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/data/Schaefer2018_100Parcels_7Networks_order_FSLMNI152_2mm.nii.gz\n'
    b'Resampling labels\n'
    b'Resampling labels\n'
    b'Resampling labels\n'
    b'[NiftiLabelsMasker.transform_single_imgs] Loading data from /private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/betaseries_wf/0759bb8ab3011a1adda5809a\n'
    b'[NiftiLabelsMasker.transform_single_imgs] Loading data from /private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/betaseries_wf/0759bb8ab3011a1adda5809a\n'
    b'[NiftiLabelsMasker.transform_single_imgs] Loading data from /private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/betaseries_wf/0759bb8ab3011a1adda5809a\n'
    b'[NiftiLabelsMasker.transform_single_imgs] Extracting region signals\n'
    b'[NiftiLabelsMasker.transform_single_imgs] Extracting region signals\n'
    b'[NiftiLabelsMasker.transform_single_imgs] Extracting region signals\n'
    b"/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/importlib/_bootstrap.py:219: ImportWarning: can't resolve package from __spec__ or __package__, falling back on __name__ and __path__\n"
    b'  return f(*args, **kwds)\n'
    b"/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/importlib/_bootstrap.py:219: ImportWarning: can't resolve package from __spec__ or __package__, falling back on __name__ and __path__\n"
    b'  return f(*args, **kwds)\n'
    b"/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/importlib/_bootstrap.py:219: ImportWarning: can't resolve package from __spec__ or __package__, falling back on __name__ and __path__\n"
    b'  return f(*args, **kwds)\n'
    b'[NiftiLabelsMasker.transform_single_imgs] Cleaning extracted signals\n'
    b'[NiftiLabelsMasker.transform_single_imgs] Cleaning extracted signals\n'
    b'[NiftiLabelsMasker.transform_single_imgs] Cleaning extracted signals\n'
    b'/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/site-packages/nipype/pipeline/engine/utils.py:307: DeprecationWarning: use "HasTraits.trait_set" instead\n'
    b'  result.outputs.set(**modify_paths(tosave, relative=True, basedir=cwd))\n'
    b'/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/site-packages/nipype/pipeline/engine/utils.py:307: DeprecationWarning: use "HasTraits.trait_set" instead\n'
    b'  result.outputs.set(**modify_paths(tosave, relative=True, basedir=cwd))\n'
    b'190415-14:40:22,76 nipype.workflow INFO:\n'
    b'\t [Node] Finished "_atlas_corr_node0".\n'
    b'190415-14:40:22,79 nipype.workflow INFO:\n'
    b'\t [Node] Finished "_atlas_corr_node2".\n'
    b'/Users/peerherholz/google_drive/GitHub/NiBetaSeries/.tox/docs/lib/python3.6/site-packages/nipype/pipeline/engine/utils.py:307: DeprecationWarning: use "HasTraits.trait_set" instead\n'
    b'  result.outputs.set(**modify_paths(tosave, relative=True, basedir=cwd))\n'
    b'190415-14:40:22,83 nipype.workflow INFO:\n'
    b'\t [Node] Finished "_atlas_corr_node1".\n'
    b'190415-14:40:22,157 nipype.workflow INFO:\n'
    b'\t [Job 4] Completed (_atlas_corr_node0).\n'
    b'190415-14:40:22,236 nipype.workflow INFO:\n'
    b'\t [Job 5] Completed (_atlas_corr_node1).\n'
    b'190415-14:40:22,236 nipype.workflow INFO:\n'
    b'\t [Job 6] Completed (_atlas_corr_node2).\n'
    b'190415-14:40:22,238 nipype.workflow INFO:\n'
    b'\t [MultiProc] Running 0 tasks, and 1 jobs ready. Free memory (GB): 10.80/10.80, Free processors: 4/4.\n'
    b'190415-14:40:22,280 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "nibetaseries_participant_wf.single_subject001_wf.correlation_wf.atlas_corr_node" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/correlation_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/atlas_corr_node".\n'
    b'190415-14:40:22,284 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_atlas_corr_node0" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/correlation_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/atlas_corr_node/mapflow/_atlas_corr_node0".\n'
    b'190415-14:40:22,286 nipype.workflow INFO:\n'
    b'\t [Node] Cached "_atlas_corr_node0" - collecting precomputed outputs\n'
    b'190415-14:40:22,286 nipype.workflow INFO:\n'
    b'\t [Node] "_atlas_corr_node0" found cached.\n'
    b'190415-14:40:22,287 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_atlas_corr_node1" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/correlation_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/atlas_corr_node/mapflow/_atlas_corr_node1".\n'
    b'190415-14:40:22,289 nipype.workflow INFO:\n'
    b'\t [Node] Cached "_atlas_corr_node1" - collecting precomputed outputs\n'
    b'190415-14:40:22,289 nipype.workflow INFO:\n'
    b'\t [Node] "_atlas_corr_node1" found cached.\n'
    b'190415-14:40:22,290 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_atlas_corr_node2" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/correlation_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/atlas_corr_node/mapflow/_atlas_corr_node2".\n'
    b'190415-14:40:22,292 nipype.workflow INFO:\n'
    b'\t [Node] Cached "_atlas_corr_node2" - collecting precomputed outputs\n'
    b'190415-14:40:22,292 nipype.workflow INFO:\n'
    b'\t [Node] "_atlas_corr_node2" found cached.\n'
    b'190415-14:40:22,296 nipype.workflow INFO:\n'
    b'\t [Node] Finished "nibetaseries_participant_wf.single_subject001_wf.correlation_wf.atlas_corr_node".\n'
    b'190415-14:40:24,161 nipype.workflow INFO:\n'
    b'\t [Job 1] Completed (nibetaseries_participant_wf.single_subject001_wf.correlation_wf.atlas_corr_node).\n'
    b'190415-14:40:24,163 nipype.workflow INFO:\n'
    b'\t [MultiProc] Running 0 tasks, and 1 jobs ready. Free memory (GB): 10.80/10.80, Free processors: 4/4.\n'
    b'190415-14:40:26,164 nipype.workflow INFO:\n'
    b'\t [MultiProc] Running 0 tasks, and 3 jobs ready. Free memory (GB): 10.80/10.80, Free processors: 4/4.\n'
    b'190415-14:40:26,202 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_rename_matrix_node0" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/correlation_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/rename_matrix_node/mapflow/_rename_matrix_node0".\n'
    b'190415-14:40:26,204 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_rename_matrix_node1" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/correlation_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/rename_matrix_node/mapflow/_rename_matrix_node1".\n'
    b'190415-14:40:26,206 nipype.workflow INFO:\n'
    b'\t [Node] Running "_rename_matrix_node0" ("nipype.interfaces.utility.wrappers.Function")\n'
    b'190415-14:40:26,207 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_rename_matrix_node2" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/correlation_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/rename_matrix_node/mapflow/_rename_matrix_node2".\n'
    b'190415-14:40:26,208 nipype.workflow INFO:\n'
    b'\t [Node] Running "_rename_matrix_node1" ("nipype.interfaces.utility.wrappers.Function")\n'
    b'190415-14:40:26,211 nipype.workflow INFO:\n'
    b'\t [Node] Running "_rename_matrix_node2" ("nipype.interfaces.utility.wrappers.Function")\n'
    b'190415-14:40:26,217 nipype.workflow INFO:\n'
    b'\t [Node] Finished "_rename_matrix_node0".\n'
    b'190415-14:40:26,218 nipype.workflow INFO:\n'
    b'\t [Node] Finished "_rename_matrix_node1".\n'
    b'190415-14:40:26,219 nipype.workflow INFO:\n'
    b'\t [Node] Finished "_rename_matrix_node2".\n'
    b'190415-14:40:28,167 nipype.workflow INFO:\n'
    b'\t [Job 7] Completed (_rename_matrix_node0).\n'
    b'190415-14:40:28,168 nipype.workflow INFO:\n'
    b'\t [Job 8] Completed (_rename_matrix_node1).\n'
    b'190415-14:40:28,168 nipype.workflow INFO:\n'
    b'\t [Job 9] Completed (_rename_matrix_node2).\n'
    b'190415-14:40:28,170 nipype.workflow INFO:\n'
    b'\t [MultiProc] Running 0 tasks, and 1 jobs ready. Free memory (GB): 10.80/10.80, Free processors: 4/4.\n'
    b'190415-14:40:28,212 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "nibetaseries_participant_wf.single_subject001_wf.correlation_wf.rename_matrix_node" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/correlation_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/rename_matrix_node".\n'
    b'190415-14:40:28,217 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_rename_matrix_node0" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/correlation_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/rename_matrix_node/mapflow/_rename_matrix_node0".\n'
    b'190415-14:40:28,219 nipype.workflow INFO:\n'
    b'\t [Node] Cached "_rename_matrix_node0" - collecting precomputed outputs\n'
    b'190415-14:40:28,219 nipype.workflow INFO:\n'
    b'\t [Node] "_rename_matrix_node0" found cached.\n'
    b'190415-14:40:28,220 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_rename_matrix_node1" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/correlation_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/rename_matrix_node/mapflow/_rename_matrix_node1".\n'
    b'190415-14:40:28,222 nipype.workflow INFO:\n'
    b'\t [Node] Cached "_rename_matrix_node1" - collecting precomputed outputs\n'
    b'190415-14:40:28,222 nipype.workflow INFO:\n'
    b'\t [Node] "_rename_matrix_node1" found cached.\n'
    b'190415-14:40:28,224 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_rename_matrix_node2" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/correlation_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/rename_matrix_node/mapflow/_rename_matrix_node2".\n'
    b'190415-14:40:28,225 nipype.workflow INFO:\n'
    b'\t [Node] Cached "_rename_matrix_node2" - collecting precomputed outputs\n'
    b'190415-14:40:28,225 nipype.workflow INFO:\n'
    b'\t [Node] "_rename_matrix_node2" found cached.\n'
    b'190415-14:40:28,230 nipype.workflow INFO:\n'
    b'\t [Node] Finished "nibetaseries_participant_wf.single_subject001_wf.correlation_wf.rename_matrix_node".\n'
    b'190415-14:40:30,171 nipype.workflow INFO:\n'
    b'\t [Job 2] Completed (nibetaseries_participant_wf.single_subject001_wf.correlation_wf.rename_matrix_node).\n'
    b'190415-14:40:30,173 nipype.workflow INFO:\n'
    b'\t [MultiProc] Running 0 tasks, and 1 jobs ready. Free memory (GB): 10.80/10.80, Free processors: 4/4.\n'
    b'190415-14:40:32,172 nipype.workflow INFO:\n'
    b'\t [MultiProc] Running 0 tasks, and 3 jobs ready. Free memory (GB): 10.80/10.80, Free processors: 4/4.\n'
    b'190415-14:40:32,210 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_ds_correlation_matrix0" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/ds_correlation_matrix/mapflow/_ds_correlation_matrix0".\n'
    b'190415-14:40:32,212 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_ds_correlation_matrix1" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/ds_correlation_matrix/mapflow/_ds_correlation_matrix1".\n'
    b'190415-14:40:32,214 nipype.workflow INFO:\n'
    b'\t [Node] Running "_ds_correlation_matrix0" ("nibetaseries.interfaces.bids.DerivativesDataSink")\n'
    b'190415-14:40:32,215 nipype.workflow INFO:\n'
    b'\t [Node] Running "_ds_correlation_matrix1" ("nibetaseries.interfaces.bids.DerivativesDataSink")\n'
    b'190415-14:40:32,217 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_ds_correlation_matrix2" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/ds_correlation_matrix/mapflow/_ds_correlation_matrix2".\n'
    b'190415-14:40:32,221 nipype.workflow INFO:\n'
    b'\t [Node] Running "_ds_correlation_matrix2" ("nibetaseries.interfaces.bids.DerivativesDataSink")\n'
    b'190415-14:40:32,222 nipype.workflow INFO:\n'
    b'\t [Node] Finished "_ds_correlation_matrix0".\n'
    b'190415-14:40:32,223 nipype.workflow INFO:\n'
    b'\t [Node] Finished "_ds_correlation_matrix1".\n'
    b'190415-14:40:32,228 nipype.workflow INFO:\n'
    b'\t [Node] Finished "_ds_correlation_matrix2".\n'
    b'190415-14:40:34,172 nipype.workflow INFO:\n'
    b'\t [Job 10] Completed (_ds_correlation_matrix0).\n'
    b'190415-14:40:34,173 nipype.workflow INFO:\n'
    b'\t [Job 11] Completed (_ds_correlation_matrix1).\n'
    b'190415-14:40:34,173 nipype.workflow INFO:\n'
    b'\t [Job 12] Completed (_ds_correlation_matrix2).\n'
    b'190415-14:40:34,175 nipype.workflow INFO:\n'
    b'\t [MultiProc] Running 0 tasks, and 1 jobs ready. Free memory (GB): 10.80/10.80, Free processors: 4/4.\n'
    b'190415-14:40:34,217 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "nibetaseries_participant_wf.single_subject001_wf.ds_correlation_matrix" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/ds_correlation_matrix".\n'
    b'190415-14:40:34,221 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_ds_correlation_matrix0" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/ds_correlation_matrix/mapflow/_ds_correlation_matrix0".\n'
    b'190415-14:40:34,226 nipype.workflow INFO:\n'
    b'\t [Node] Running "_ds_correlation_matrix0" ("nibetaseries.interfaces.bids.DerivativesDataSink")\n'
    b'190415-14:40:34,269 nipype.workflow INFO:\n'
    b'\t [Node] Finished "_ds_correlation_matrix0".\n'
    b'190415-14:40:34,271 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_ds_correlation_matrix1" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/ds_correlation_matrix/mapflow/_ds_correlation_matrix1".\n'
    b'190415-14:40:34,275 nipype.workflow INFO:\n'
    b'\t [Node] Running "_ds_correlation_matrix1" ("nibetaseries.interfaces.bids.DerivativesDataSink")\n'
    b'190415-14:40:34,327 nipype.workflow INFO:\n'
    b'\t [Node] Finished "_ds_correlation_matrix1".\n'
    b'190415-14:40:34,328 nipype.workflow INFO:\n'
    b'\t [Node] Setting-up "_ds_correlation_matrix2" in "/private/var/folders/7w/skj0rj1d4hgdhxl6813xkc6h0000gn/T/tmppvvwl83a/ds000164/derivatives/work/NiBetaSeries_work/nibetaseries_participant_wf/single_subject001_wf/0759bb8ab3011a1adda5809aa6d07aab8d568e7d/ds_correlation_matrix/mapflow/_ds_correlation_matrix2".\n'
    b'190415-14:40:34,332 nipype.workflow INFO:\n'
    b'\t [Node] Running "_ds_correlation_matrix2" ("nibetaseries.interfaces.bids.DerivativesDataSink")\n'
    b'190415-14:40:34,393 nipype.workflow INFO:\n'
    b'\t [Node] Finished "_ds_correlation_matrix2".\n'
    b'190415-14:40:34,518 nipype.workflow INFO:\n'
    b'\t [Node] Finished "nibetaseries_participant_wf.single_subject001_wf.ds_correlation_matrix".\n'
    b'190415-14:40:36,175 nipype.workflow INFO:\n'
    b'\t [Job 3] Completed (nibetaseries_participant_wf.single_subject001_wf.ds_correlation_matrix).\n'
    b'190415-14:40:36,177 nipype.workflow INFO:\n'
    b'\t [MultiProc] Running 0 tasks, and 0 jobs ready. Free memory (GB): 10.80/10.80, Free processors: 4/4.\n'


Observe generated outputs
=========================


.. code-block:: default


    list_files(data_dir)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    tmppvvwl83a/
        ds000164/
            CHANGES
            dataset_description.json
            README
            T1w.json
            task-stroop_bold.json
            task-stroop_events.json
            derivatives/
                data/
                    Schaefer2018_100Parcels_7Networks_order.tsv
                    Schaefer2018_100Parcels_7Networks_order.txt
                    Schaefer2018_100Parcels_7Networks_order_FSLMNI152_2mm.nii.gz
                fmriprep/
                    sub-001/
                        func/
                            sub-001_task-stroop_bold_confounds.tsv
                            sub-001_task-stroop_bold_space-MNI152NLin2009cAsym_brainmask.nii.gz
                            sub-001_task-stroop_bold_space-MNI152NLin2009cAsym_preproc.nii.gz
                NiBetaSeries/
                    logs/
                    nibetaseries/
                        sub-001/
                            func/
                                sub-001_task-stroop_bold_space-MNI152NLin2009cAsym_preproc_trialtype-congruent_matrix.tsv
                                sub-001_task-stroop_bold_space-MNI152NLin2009cAsym_preproc_trialtype-incongruent_matrix.tsv
                                sub-001_task-stroop_bold_space-MNI152NLin2009cAsym_preproc_trialtype-neutral_matrix.tsv
                work/
                    NiBetaSeries_work/
                        nibetaseries_participant_wf/
                            d3.js
                            graph.json
                            graph1.json
                            index.html
                            single_subject001_wf/
                                0759bb8ab3011a1adda5809aa6d07aab8d568e7d/
                                    ds_correlation_matrix/
                                        _0x9c0dcdb661b1a0a711c8b49926e2fc59.json
                                        _inputs.pklz
                                        _node.pklz
                                        result_ds_correlation_matrix.pklz
                                        _report/
                                            report.rst
                                        mapflow/
                                            _ds_correlation_matrix0/
                                                _0xa0b5479eb7b49af6c05cc5b2417550e9.json
                                                _inputs.pklz
                                                _node.pklz
                                                result__ds_correlation_matrix0.pklz
                                                _report/
                                                    report.rst
                                            _ds_correlation_matrix1/
                                                _0xd9b4d9c77b2f3448c9692ace7e745784.json
                                                _inputs.pklz
                                                _node.pklz
                                                result__ds_correlation_matrix1.pklz
                                                _report/
                                                    report.rst
                                            _ds_correlation_matrix2/
                                                _0x82a2f3969a419314bef2cb2d02aa73ad.json
                                                _inputs.pklz
                                                _node.pklz
                                                result__ds_correlation_matrix2.pklz
                                                _report/
                                                    report.rst
                                betaseries_wf/
                                    0759bb8ab3011a1adda5809aa6d07aab8d568e7d/
                                        betaseries_node/
                                            _0x5185e8b09f68a4319adf77e378c34a71.json
                                            _inputs.pklz
                                            _node.pklz
                                            betaseries_trialtype-congruent.nii.gz
                                            betaseries_trialtype-incongruent.nii.gz
                                            betaseries_trialtype-neutral.nii.gz
                                            result_betaseries_node.pklz
                                            _report/
                                                report.rst
                                correlation_wf/
                                    0759bb8ab3011a1adda5809aa6d07aab8d568e7d/
                                        atlas_corr_node/
                                            _0x0252a3bc56a1fb79763974777260a507.json
                                            _inputs.pklz
                                            _node.pklz
                                            result_atlas_corr_node.pklz
                                            _report/
                                                report.rst
                                            mapflow/
                                                _atlas_corr_node0/
                                                    _0x40dc2a403b5ff6c4aa9f594f20dd5236.json
                                                    _inputs.pklz
                                                    _node.pklz
                                                    fisher_z_correlation.tsv
                                                    result__atlas_corr_node0.pklz
                                                    _report/
                                                        report.rst
                                                _atlas_corr_node1/
                                                    _0xc3b3605433af423065ae4bf6f705ba0b.json
                                                    _inputs.pklz
                                                    _node.pklz
                                                    fisher_z_correlation.tsv
                                                    result__atlas_corr_node1.pklz
                                                    _report/
                                                        report.rst
                                                _atlas_corr_node2/
                                                    _0x6b0d991f9a48fc0e7a57fe6b46ce13e6.json
                                                    _inputs.pklz
                                                    _node.pklz
                                                    fisher_z_correlation.tsv
                                                    result__atlas_corr_node2.pklz
                                                    _report/
                                                        report.rst
                                        rename_matrix_node/
                                            _0xcb523758d9d3437824f8f37cf3ecb742.json
                                            _inputs.pklz
                                            _node.pklz
                                            result_rename_matrix_node.pklz
                                            _report/
                                                report.rst
                                            mapflow/
                                                _rename_matrix_node0/
                                                    _0xea6c5cd2af80339bc390c477735a5859.json
                                                    _inputs.pklz
                                                    _node.pklz
                                                    correlation-matrix_trialtype-neutral.tsv
                                                    result__rename_matrix_node0.pklz
                                                    _report/
                                                        report.rst
                                                _rename_matrix_node1/
                                                    _0xbd69e7a0fc1ed4bca517afefc8668473.json
                                                    _inputs.pklz
                                                    _node.pklz
                                                    correlation-matrix_trialtype-congruent.tsv
                                                    result__rename_matrix_node1.pklz
                                                    _report/
                                                        report.rst
                                                _rename_matrix_node2/
                                                    _0xf8a3f2f9fd8945d0f0e01c6bbf5ac9fc.json
                                                    _inputs.pklz
                                                    _node.pklz
                                                    correlation-matrix_trialtype-incongruent.tsv
                                                    result__rename_matrix_node2.pklz
                                                    _report/
                                                        report.rst
            sub-001/
                anat/
                    sub-001_T1w.nii.gz
                func/
                    sub-001_task-stroop_bold.nii.gz
                    sub-001_task-stroop_events.tsv


Collect results
===============


.. code-block:: default


    corr_mat_path = os.path.join(out_dir, "NiBetaSeries", "nibetaseries", "sub-001", "func")
    trial_types = ['congruent', 'incongruent', 'neutral']
    filename_template = "sub-001_task-stroop_bold_space-MNI152NLin2009cAsym_preproc_trialtype-{trial_type}_matrix.tsv"
    pd_dict = {}
    for trial_type in trial_types:
        file_path = os.path.join(corr_mat_path, filename_template.format(trial_type=trial_type))
        pd_dict[trial_type] = pd.read_csv(file_path, sep='\t', na_values="n/a", index_col=0)
    # display example matrix
    print(pd_dict[trial_type].head())





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    LH_Vis_1  LH_Vis_2  LH_Vis_3  LH_Vis_4  ...  RH_Default_PFCm_2  RH_Default_PFCm_3  RH_Default_PCC_1  RH_Default_PCC_2
    LH_Vis_1       NaN  0.092135 -0.003990  0.075498  ...           0.196831           0.343553          0.095624          0.016799
    LH_Vis_2  0.092135       NaN  0.216346 -0.088788  ...           0.032079           0.086436         -0.119613         -0.007679
    LH_Vis_3 -0.003990  0.216346       NaN  0.121108  ...           0.193366           0.207421          0.202673          0.177828
    LH_Vis_4  0.075498 -0.088788  0.121108       NaN  ...           0.378814           0.258830         -0.019256         -0.034034
    LH_Vis_5  0.314494  0.354525  0.024211  0.391487  ...           0.252374           0.382709         -0.235334          0.032317

    [5 rows x 100 columns]


Graph the results
=================


.. code-block:: default


    fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True, sharey=True, figsize=(10, 30),
                             gridspec_kw={'wspace': 0.025, 'hspace': 0.075})

    cbar_ax = fig.add_axes([.91, .3, .03, .4])
    r = 0
    for trial_type, df in pd_dict.items():
        g = sns.heatmap(df, ax=axes[r], vmin=-.5, vmax=1., square=True,
                        cbar=True, cbar_ax=cbar_ax)
        axes[r].set_title(trial_type)
        # iterate over rows
        r += 1
    plt.tight_layout()



.. image:: /auto_examples/images/sphx_glr_plot_run_nibetaseries_001.png
    :class: sphx-glr-single-img





.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 2 minutes  33.297 seconds)


.. _sphx_glr_download_auto_examples_plot_run_nibetaseries.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download

     :download:`Download Python source code: plot_run_nibetaseries.py <plot_run_nibetaseries.py>`



  .. container:: sphx-glr-download

     :download:`Download Jupyter notebook: plot_run_nibetaseries.ipynb <plot_run_nibetaseries.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.readthedocs.io>`_
