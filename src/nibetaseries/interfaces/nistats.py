#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import logging
from nipype.interfaces.base import (
    BaseInterfaceInputSpec, TraitedSpec,
    OutputMultiPath, File, LibraryBaseInterface,
    SimpleInterface, traits
    )


class NistatsBaseInterface(LibraryBaseInterface):
    _pkg = 'nistats'


class LSSBetaSeriesInputSpec(BaseInterfaceInputSpec):
    bold_file = File(exists=True, mandatory=True,
                     desc="The bold run")
    bold_metadata = traits.Dict(desc='Dictionary containing useful information about'
                                ' the bold_file')
    mask_file = File(exists=True, mandatory=True,
                     desc="Binarized nifti file indicating the brain")
    events_file = File(exists=True, mandatory=True,
                       desc="File that contains all events from the bold run")
    confounds_file = traits.Either(None, File(exists=True),
                                   desc="File that contains all usable confounds")
    selected_confounds = traits.Either(None, traits.List(),
                                       desc="Column names of the regressors to include")
    hrf_model = traits.String(desc="hemodynamic response model")
    smoothing_kernel = traits.Either(None, traits.Float(),
                                     desc="full wide half max smoothing kernel")
    high_pass = traits.Float(0.0078125, desc="the high pass filter (Hz)")
    fir_delays = traits.Either(None, traits.List(traits.Int),
                               desc="FIR delays (in scans)")


class LSSBetaSeriesOutputSpec(TraitedSpec):
    beta_maps = OutputMultiPath(File)
    design_matrices = traits.Dict()


class LSSBetaSeries(NistatsBaseInterface, SimpleInterface):
    """Calculates BetaSeries Maps From a BOLD file (one series map per event type)."""
    input_spec = LSSBetaSeriesInputSpec
    output_spec = LSSBetaSeriesOutputSpec

    def _run_interface(self, runtime):
        from nistats import first_level_model
        import nibabel as nib
        import os

        # get t_r from bold_metadata
        t_r = self.inputs.bold_metadata['RepetitionTime']

        # get the confounds:
        if self.inputs.confounds_file and self.inputs.selected_confounds:
            confounds = _select_confounds(self.inputs.confounds_file,
                                          self.inputs.selected_confounds)
        else:
            confounds = None

        # high_pass, switch from Hz to Period
        high_pass_period = int(1 / self.inputs.high_pass)

        # setup the model
        model = first_level_model.FirstLevelModel(
            t_r=t_r,
            slice_time_ref=0,
            hrf_model=self.inputs.hrf_model,
            mask=self.inputs.mask_file,
            smoothing_fwhm=self.inputs.smoothing_kernel,
            standardize=True,
            signal_scaling=0,
            period_cut=high_pass_period,
            drift_model='cosine',
            verbose=1,
            fir_delays=self.inputs.fir_delays,
        )

        # initialize dictionary to contain trial estimates (betas)
        beta_maps = {}
        design_matrix_collector = {}
        for target_trial_df, trial_type, trial_idx in \
                _lss_events_iterator(self.inputs.events_file):

            # fit the model for the target trial
            model.fit(self.inputs.bold_file,
                      events=target_trial_df,
                      confounds=confounds)

            if self.inputs.hrf_model == 'fir':
                # FS modeling
                for delay in self.inputs.fir_delays:
                    delay_ttype = trial_type+'_delay_{}'.format(delay)
                    new_delay_ttype = delay_ttype.replace('_delay_{}'.format(delay),
                                                          'Delay{}Vol'.format(delay))
                    beta_map = model.compute_contrast(
                        delay_ttype, output_type='effect_size')
                    if new_delay_ttype in beta_maps:
                        beta_maps[new_delay_ttype].append(beta_map)
                    else:
                        beta_maps[new_delay_ttype] = [beta_map]
            else:
                # calculate the beta map
                beta_map = model.compute_contrast(trial_type, output_type='effect_size')
                design_matrix_collector[trial_idx] = model.design_matrices_[0]
                # import pdb; pdb.set_trace()
                # assign beta map to appropriate list
                if trial_type in beta_maps:
                    beta_maps[trial_type].append(beta_map)
                else:
                    beta_maps[trial_type] = [beta_map]

        # make a beta series from each beta map list
        beta_series_template = os.path.join(runtime.cwd,
                                            'desc-{trial_type}_betaseries.nii.gz')
        # collector for the betaseries files
        beta_series_lst = []
        for t_type, betas in beta_maps.items():
            size_check = len(betas)
            if size_check < 3:
                logging.warning(
                    'At least 3 trials are needed '
                    'for a beta series: {trial_type} has {num}'.format(trial_type=t_type,
                                                                       num=size_check))
            else:
                beta_series = nib.funcs.concat_images(betas)
                nib.save(beta_series, beta_series_template.format(trial_type=t_type))
                beta_series_lst.append(beta_series_template.format(trial_type=t_type))

        self._results['beta_maps'] = beta_series_lst
        self._results['design_matrices'] = design_matrix_collector
        return runtime


class LSABetaSeriesInputSpec(BaseInterfaceInputSpec):
    bold_file = File(exists=True, mandatory=True,
                     desc="The bold run")
    bold_metadata = traits.Dict(desc='Dictionary containing useful information about'
                                ' the bold_file')
    mask_file = File(exists=True, mandatory=True,
                     desc="Binarized nifti file indicating the brain")
    events_file = File(exists=True, mandatory=True,
                       desc="File that contains all events from the bold run")
    confounds_file = traits.Either(None, File(exists=True),
                                   desc="File that contains all usable confounds")
    selected_confounds = traits.Either(None, traits.List(),
                                       desc="Column names of the regressors to include")
    hrf_model = traits.String(desc="hemodynamic response model")
    smoothing_kernel = traits.Either(None, traits.Float(),
                                     desc="full wide half max smoothing kernel")
    high_pass = traits.Float(0.0078125, desc="the high pass filter (Hz)")


class LSABetaSeriesOutputSpec(TraitedSpec):
    beta_maps = OutputMultiPath(File)
    design_matrices = traits.List()


class LSABetaSeries(NistatsBaseInterface, SimpleInterface):
    """Calculates BetaSeries Maps From a BOLD file (one series map per event type)."""
    input_spec = LSABetaSeriesInputSpec
    output_spec = LSABetaSeriesOutputSpec

    def _run_interface(self, runtime):
        from nistats import first_level_model
        import nibabel as nib
        import os

        # get t_r from bold_metadata
        t_r = self.inputs.bold_metadata['RepetitionTime']

        # get the confounds:
        if self.inputs.confounds_file and self.inputs.selected_confounds:
            confounds = _select_confounds(self.inputs.confounds_file,
                                          self.inputs.selected_confounds)
        else:
            confounds = None

        # high_pass, switch from Hz to Period
        high_pass_period = int(1 / self.inputs.high_pass)

        # setup the model
        model = first_level_model.FirstLevelModel(
            t_r=t_r,
            slice_time_ref=0,
            hrf_model=self.inputs.hrf_model,
            mask=self.inputs.mask_file,
            smoothing_fwhm=self.inputs.smoothing_kernel,
            standardize=True,
            signal_scaling=0,
            period_cut=high_pass_period,
            drift_model='cosine',
            verbose=1
        )

        # initialize dictionary to contain trial estimates (betas)
        beta_maps = {}
        lsa_df = _lsa_events_converter(self.inputs.events_file)
        model.fit(self.inputs.bold_file, events=lsa_df, confounds=confounds)
        design_matrix = model.design_matrices_[0]
        for i_trial in lsa_df.index:
            t_name = lsa_df.loc[i_trial, 'trial_type']
            t_type = lsa_df.loc[i_trial, 'original_trial_type']

            # calculate the beta map
            beta_map = model.compute_contrast(t_name, output_type='effect_size')

            # assign beta map to appropriate list
            if t_type in beta_maps:
                beta_maps[t_type].append(beta_map)
            else:
                beta_maps[t_type] = [beta_map]

        # make a beta series from each beta map list
        beta_series_template = os.path.join(runtime.cwd,
                                            'desc-{trial_type}_betaseries.nii.gz')
        # collector for the betaseries files
        beta_series_lst = []
        for t_type, betas in beta_maps.items():
            size_check = len(betas)
            if size_check < 3:
                logging.warning(
                    'At least 3 trials are needed '
                    'for a beta series: {trial_type} has {num}'.format(trial_type=t_type,
                                                                       num=size_check))
            else:
                beta_series = nib.funcs.concat_images(betas)
                nib.save(beta_series, beta_series_template.format(trial_type=t_type))
                beta_series_lst.append(beta_series_template.format(trial_type=t_type))

        self._results['beta_maps'] = beta_series_lst
        self._results['design_matrices'] = [design_matrix]
        return runtime


def _lsa_events_converter(events_file):
    """Make a model where each trial has its own regressor using least squares
    all (LSA)

    Parameters
    ----------
    events_file : str
        File that contains all events from the bold run

    Yields
    ------
    events : DataFrame
        A DataFrame in which each trial has its own trial_type
    """

    import pandas as pd
    events = pd.read_csv(events_file, sep='\t')
    events['original_trial_type'] = events['trial_type']
    for cond, cond_df in events.groupby('trial_type'):
        cond_idx = cond_df.index
        for i_trial, trial_idx in enumerate(cond_idx):
            trial_name = '{0}_{1:04d}'.format(cond, i_trial+1)
            events.loc[trial_idx, 'trial_type'] = trial_name
    return events


def _lss_events_iterator(events_file):
    """Make a model for each trial using least squares separate (LSS)

    Parameters
    ----------
    events_file : str
        File that contains all events from the bold run

    Yields
    ------
    events_trial : DataFrame
        A DataFrame in which the target trial maintains its trial type,
        but all other trials are assigned to 'other'
    trial_type : str
        The trial_type of the target trial
    trial_counter : int
        The marker for the nth trial of that type
    """

    import pandas as pd
    import numpy as np
    events = pd.read_csv(events_file, sep='\t')
    trial_counter = dict([(t, 0) for t in np.unique(events['trial_type'])])
    for trial_id in range(len(events)):
        trial_type = events.loc[trial_id, 'trial_type']
        # make a copy of the dataframe
        events_trial = events.copy()
        # assign new name to all events from original condition
        trial_type_id = events_trial['trial_type'] == trial_type
        events_trial.loc[trial_type_id, 'trial_type'] = 'other'
        # assign the trial of interest to be its original value
        events_trial.loc[trial_id, 'trial_type'] = trial_type
        yield events_trial, trial_type, trial_counter[trial_type]
        trial_counter[trial_type] += 1


def _select_confounds(confounds_file, selected_confounds):
    """Process and return selected confounds from the confounds file

    Parameters
    ----------
    confounds_file : str
        File that contains all usable confounds
    selected_confounds : list
        List containing all desired confounds

    Returns
    -------
    desired_confounds : DataFrame
        contains all desired (processed) confounds.
    """
    import pandas as pd
    import numpy as np
    confounds_df = pd.read_csv(confounds_file, sep='\t', na_values='n/a')

    # fill the first value of FramewiseDisplacement with the mean.
    if 'FramewiseDisplacement' in selected_confounds:
        confounds_df['FramewiseDisplacement'] = confounds_df['FramewiseDisplacement'].fillna(
                                np.mean(confounds_df['FramewiseDisplacement']))

    desired_confounds = confounds_df[selected_confounds]
    return desired_confounds
