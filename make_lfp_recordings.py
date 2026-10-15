from pathlib import Path
import spikeinterface.full as si
import probeinterface as pi
import pandas as pd
import numpy as np

from .config import experiment_path, epoch_name_to_shank, probe_names

for probe_name in probe_names:

    data_folder = Path(f'processed/{probe_name}')

    for epoch_name, probe_place in epoch_name_to_shank:

        epoch_path = experiment_path / f'{epoch_name}/NeuropixelsV2'

        ephys_path = epoch_path / f'NeuropixelsV2_{probe_name}_0.arrow'
        probe_path = list(epoch_path.glob('*.json'))[0]

        rec = si.unsigned_to_signed(si.read_bonsai_onix_arrow(str(ephys_path), sampling_frequency=30_000))

        probe = pi.read_probeinterface(probe_path)
        rec.set_probegroup(probe)

        half_rec = rec.select_channels(rec.channel_ids[rec.get_channel_locations()[:,0] == rec.get_channel_locations()[0][0]])

        pp_rec = si.decimate(si.bandpass_filter(si.common_reference(half_rec), freq_min=0.5, freq_max = 300, ignore_low_freq_error=True, margin_ms=12_000), decimation_factor=50)

        pp_rec.save(format='binary', folder=f'{probe_name}/{probe_name}_{epoch_name_to_shank[epoch_name]}_lfp', n_jobs=4, overwrite=True, chunk_duration='30s')
