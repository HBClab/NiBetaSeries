#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
from nipype.interfaces.base import (
    BaseInterfaceInputSpec, TraitedSpec,
    OutputMultiPath, File, LibraryBaseInterface,
    SimpleInterface, traits
    )
import nibabel as nib


class NistatsBaseInterface(LibraryBaseInterface):
    _pkg = 'nistats'


class LSSBetaSeriesInputSpec(BaseInterfaceInputSpec):
    bold_file = traits.Either(File(exists=True, mandatory=True,
                                   desc="The bold run"),
                              nib.spatialimages.SpatialImage)
    bold_metadata = traits.Dict(desc='Dictionary containing useful information about'
                                ' the bold_file')
    mask_file = traits.Either(File(exists=True, mandatory=True,
                              desc="Binarized nifti file indicating the brain"),
                              nib.spatialimages.SpatialImage)
    events_file = File(exists=True, mandatory=True,
                       desc="File that contains all events from the bold run")
    confounds_file = traits.Either(None, File(exists=True),
                                   desc="File that contains all usable confounds")
    signal_scaling = traits.Enum(False, 0,
                                 desc="Whether (0) or not (False) to scale each"
                                      " voxel's timeseries")
    selected_confounds = traits.Either(None, traits.List(),
                                       desc="Column names of the regressors to include")
    hrf_model = traits.String(desc="hemodynamic response model")
    smoothing_kernel = traits.Either(None, traits.Float(),
                                     desc="full wide half max smoothing kernel")
    high_pass = traits.Float(0.0078125, desc="the high pass filter (Hz)")
    fir_delays = traits.Either(None, traits.List(traits.Int),
                               desc="FIR delays (in scans)",
                               default=None, usedefault=True)
    return_tstat = traits.Bool(desc="use the T-statistic instead of the raw beta estimates")


class LSSBetaSeriesOutputSpec(TraitedSpec):
    beta_maps = OutputMultiPath(File)
    design_matrices = traits.Dict()
    residual = traits.File(exists=True)


class LSSBetaSeries(NistatsBaseInterface, SimpleInterface):
    """Calculates BetaSeries Maps From a BOLD file (one series map per event type)."""
    input_spec = LSSBetaSeriesInputSpec
    output_spec = LSSBetaSeriesOutputSpec

    def _run_interface(self, runtime):
        from nistats import first_level_model
        import os

        # get t_r from bold_metadata
        t_r = self.inputs.bold_metadata['RepetitionTime']

        # get the confounds:
        if self.inputs.confounds_file and self.inputs.selected_confounds:
            confounds = _select_confounds(self.inputs.confounds_file,
                                          self.inputs.selected_confounds)
        else:
            confounds = None

        # setup the model
        model = first_level_model.FirstLevelModel(
            t_r=t_r,
            slice_time_ref=0,
            hrf_model=self.inputs.hrf_model,
            mask=self.inputs.mask_file,
            smoothing_fwhm=self.inputs.smoothing_kernel,
            signal_scaling=self.inputs.signal_scaling,
            high_pass=self.inputs.high_pass,
            drift_model='cosine',
            verbose=1,
            fir_delays=self.inputs.fir_delays,
            minimize_memory=False,
        )

        # initialize dictionary to contain trial estimates (betas)
        beta_maps = {}
        residuals = None
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
                    beta_map = _calc_beta_map(model,
                                              delay_ttype,
                                              self.inputs.hrf_model,
                                              self.inputs.return_tstat)
                    if new_delay_ttype in beta_maps:
                        beta_maps[new_delay_ttype].append(beta_map)
                    else:
                        beta_maps[new_delay_ttype] = [beta_map]
            else:
                # calculate the beta map
                beta_map = _calc_beta_map(model,
                                          trial_type,
                                          self.inputs.hrf_model,
                                          self.inputs.return_tstat)
                design_matrix_collector[trial_idx] = model.design_matrices_[0]
                # assign beta map to appropriate list
                if trial_type in beta_maps:
                    beta_maps[trial_type].append(beta_map)
                else:
                    beta_maps[trial_type] = [beta_map]

            # add up all the residuals (to be divided later)
            if residuals is None:
                residuals = model.residuals[0].get_fdata()
            else:
                residuals += model.residuals[0].get_fdata()

        # make an average residual
        ave_residual = residuals / (trial_idx + 1)
        # make residual nifti image
        residual_file = os.path.join(runtime.cwd, 'desc-residuals_bold.nii.gz')
        nib.Nifti2Image(
            ave_residual,
            model.residuals[0].affine,
            model.residuals[0].header,
        ).to_filename(residual_file)
        # make a beta series from each beta map list
        beta_series_template = os.path.join(runtime.cwd,
                                            'desc-{trial_type}_betaseries.nii.gz')
        # collector for the betaseries files
        beta_series_lst = []
        for t_type, betas in beta_maps.items():
            beta_series = nib.funcs.concat_images(betas)
            nib.save(beta_series, beta_series_template.format(trial_type=t_type))
            beta_series_lst.append(beta_series_template.format(trial_type=t_type))

        self._results['beta_maps'] = beta_series_lst
        self._results['design_matrices'] = design_matrix_collector
        self._results['residual'] = residual_file
        return runtime


class LSABetaSeriesInputSpec(BaseInterfaceInputSpec):
    bold_file = traits.Either(File(exists=True, mandatory=True,
                                   desc="The bold run"),
                              nib.spatialimages.SpatialImage)
    bold_metadata = traits.Dict(desc='Dictionary containing useful information about'
                                ' the bold_file')
    mask_file = traits.Either(File(exists=True, mandatory=True,
                              desc="Binarized nifti file indicating the brain"),
                              nib.spatialimages.SpatialImage)
    events_file = File(exists=True, mandatory=True,
                       desc="File that contains all events from the bold run")
    confounds_file = traits.Either(None, File(exists=True),
                                   desc="File that contains all usable confounds")
    signal_scaling = traits.Enum(False, 0,
                                 desc="Whether (0) or not (False) to scale each"
                                      " voxel's timeseries")
    selected_confounds = traits.Either(None, traits.List(),
                                       desc="Column names of the regressors to include")
    hrf_model = traits.String(desc="hemodynamic response model")
    smoothing_kernel = traits.Either(None, traits.Float(),
                                     desc="full wide half max smoothing kernel")
    high_pass = traits.Float(0.0078125, desc="the high pass filter (Hz)")
    return_tstat = traits.Bool(desc="use the T-statistic instead of the raw beta estimates")


class LSABetaSeriesOutputSpec(TraitedSpec):
    beta_maps = OutputMultiPath(File)
    design_matrices = traits.List()
    residual = traits.File(exists=True)


class LSABetaSeries(NistatsBaseInterface, SimpleInterface):
    """Calculates BetaSeries Maps From a BOLD file (one series map per event type)."""
    input_spec = LSABetaSeriesInputSpec
    output_spec = LSABetaSeriesOutputSpec

    def _run_interface(self, runtime):
        from nistats import first_level_model
        import os

        # get t_r from bold_metadata
        t_r = self.inputs.bold_metadata['RepetitionTime']

        # get the confounds:
        if self.inputs.confounds_file and self.inputs.selected_confounds:
            confounds = _select_confounds(self.inputs.confounds_file,
                                          self.inputs.selected_confounds)
        else:
            confounds = None

        # setup the model
        model = first_level_model.FirstLevelModel(
            t_r=t_r,
            slice_time_ref=0,
            hrf_model=self.inputs.hrf_model,
            mask=self.inputs.mask_file,
            smoothing_fwhm=self.inputs.smoothing_kernel,
            signal_scaling=self.inputs.signal_scaling,
            high_pass=self.inputs.high_pass,
            drift_model='cosine',
            verbose=1,
            minimize_memory=False,
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
            beta_map = _calc_beta_map(model,
                                      t_name,
                                      self.inputs.hrf_model,
                                      self.inputs.return_tstat)

            # assign beta map to appropriate list
            if t_type in beta_maps:
                beta_maps[t_type].append(beta_map)
            else:
                beta_maps[t_type] = [beta_map]

        # calculate the residual
        residual_file = os.path.join(runtime.cwd, 'desc-residuals_bold.nii.gz')
        model.residuals[0].to_filename(residual_file)
        # make a beta series from each beta map list
        beta_series_template = os.path.join(runtime.cwd,
                                            'desc-{trial_type}_betaseries.nii.gz')
        # collector for the betaseries files
        beta_series_lst = []
        for t_type, betas in beta_maps.items():
            beta_series = nib.funcs.concat_images(betas)
            nib.save(beta_series, beta_series_template.format(trial_type=t_type))
            beta_series_lst.append(beta_series_template.format(trial_type=t_type))

        self._results['beta_maps'] = beta_series_lst
        self._results['design_matrices'] = [design_matrix]
        self._results['residual'] = residual_file
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
        List containing all desired confounds.
        confounds can be listed as regular expressions (e.g., "motion_outlier.*")

    Returns
    -------
    desired_confounds : DataFrame
        contains all desired (processed) confounds.
    """
    import pandas as pd
    import numpy as np
    import re

    confounds_df = pd.read_csv(confounds_file, sep='\t', na_values='n/a')
    # regular expression to capture confounds specified at the command line
    confound_expr = re.compile(r"|".join(selected_confounds))
    expanded_confounds = list(filter(confound_expr.fullmatch, confounds_df.columns))
    imputables = ('framewise_displacement', 'std_dvars', 'dvars', '.*derivative1.*')

    # regular expression to capture all imputable confounds
    impute_expr = re.compile(r"|".join(imputables))
    expanded_imputables = list(filter(impute_expr.fullmatch, expanded_confounds))
    for imputable in expanded_imputables:
        vals = confounds_df[imputable].values
        if not np.isnan(vals[0]):
            continue
        # Impute the mean non-zero, non-NaN value
        confounds_df[imputable][0] = np.nanmean(vals[vals != 0])

    desired_confounds = confounds_df[expanded_confounds]
    # check to see if there are any remaining nans
    if desired_confounds.isna().values.any():
        msg = "The selected confounds contain nans: {conf}".format(conf=expanded_confounds)
        raise ValueError(msg)
    return desired_confounds


def _calc_beta_map(model, trial_type, hrf_model, tstat):
    """
    Calculates the beta estimates for every voxel from
    a nistats model

    Parameters
    ----------
    model : nistats.first_level_model.FirstLevelModel
        a fit model of the first level results
    trial_type : str
        the trial to create the beta estimate
    hrf_model : str
        the hemondynamic response function used to fit the model
    tstat : bool
        return the t-statistic for the betas instead of the raw estimates

    Returns
    -------
    beta_map : nibabel.nifti2.Nifti2Image
        nifti image containing voxelwise beta estimates
    """
    import numpy as np

    # make it so we do not divide by zero
    TINY = 1e-50
    raw_beta_map = _estimate_map(model, trial_type, hrf_model, 'effect_size')
    if tstat:
        var_map = _estimate_map(model, trial_type, hrf_model, 'effect_variance')
        tstat_array = raw_beta_map.get_fdata() / np.sqrt(np.maximum(var_map.get_fdata(), TINY))
        return nib.Nifti2Image(tstat_array, raw_beta_map.affine, raw_beta_map.header)
    else:
        return raw_beta_map


def _estimate_map(model, trial_type, hrf_model, output_type):
    """
    Calculates model output for every voxel from
    a nistats model

    Parameters
    ----------
    model : nistats.first_level_model.FirstLevelModel
        a fit model of the first level results
    trial_type : str
        the trial to create the beta estimate
    hrf_model : str
        the hemondynamic response function used to fit the model
    output_type : str
        Type of the output map.
        Can be ‘z_score’, ‘stat’, ‘p_value’, ‘effect_size’, or ‘effect_variance’

    Returns
    -------
    map_img : nibabel.nifti2.Nifti2Image
        nifti image containing voxelwise output_type estimates
    """
    import numpy as np

    # calculate the beta map
    map_list = []
    map_base = model.compute_contrast(trial_type, output_type=output_type)
    map_list.append(map_base.get_fdata())
    sign = np.where(map_list[0] < 0, -1, 1)
    if 'derivative' in hrf_model:
        td_contrast = '_'.join([trial_type, 'derivative'])
        map_list.append(
            model.compute_contrast(
                td_contrast, output_type=output_type).get_fdata())
    if 'dispersion' in hrf_model:
        dd_contrast = '_'.join([trial_type, 'dispersion'])
        map_list.append(
            model.compute_contrast(
                dd_contrast, output_type=output_type).get_fdata())

    if len(map_list) == 1:
        map_img = map_base
    else:
        map_array = sign * \
            np.sqrt(
                np.sum(
                    np.array([np.power(c, 2) for c in map_list]), axis=0))

        map_img = nib.Nifti2Image(
            map_array,
            map_base.affine,
            map_base.header)

    return map_img
