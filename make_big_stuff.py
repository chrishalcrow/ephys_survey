import numpy as np
from pathlib import Path
import spikeinterface.full as si
import probeinterface as pi

from utils import read_bonsai_onix_arrow
from config import experiment_path, epoch_name_to_shank, probe_names, mouse_name

si.set_global_job_kwargs(n_jobs=4)

import argparse

print(experiment_path)

parser = argparse.ArgumentParser(
    description="Process probe and shank indices."
)

# Positional arguments (or prefix with -- for optional flags)
parser.add_argument(
    "probe_index",
    type=int,
    help="Zero-based index of the probe",
)
parser.add_argument(
    "shank_index",
    type=int,
    help="Zero-based index of the shank",
)

args = parser.parse_args()

probe_index = args.probe_index
shank_index = args.shank_index

probe_name = probe_names[probe_index]

data_folder = Path(f'processed/{mouse_name}/{probe_name}')

epoch_name = list(epoch_name_to_shank.keys())[shank_index]
probe_place = list(epoch_name_to_shank.values())[shank_index]

epoch_path = experiment_path / f'{epoch_name}/NeuropixelsV2'

print(epoch_path)

ephys_path = epoch_path / f'NeuropixelsV2_{probe_name}_0.arrow'
probe_path = list(epoch_path.glob('*.json'))[0]

rec = si.unsigned_to_signed(
    read_bonsai_onix_arrow(
        str(ephys_path), 
        sampling_frequency=30_000,
        gain_to_uV=3.05176,
        offset_to_uV=0.0,
    )
)

probe = pi.read_probeinterface(probe_path)
rec.set_probegroup(probe)

probe_map = si.plot_probe_map(rec)
probe_map.figure.savefig(data_folder / f'{probe_place}_probe.png')

# make LFP recording
half_rec = rec.select_channels(rec.channel_ids[rec.get_channel_locations()[:,0] == rec.get_channel_locations()[0][0]])
lfp_rec = si.decimate(si.bandpass_filter(half_rec, freq_min=0.5, freq_max = 300, ignore_low_freq_error=True, margin_ms=12_000), decimation_factor=50)
#lfp_rec.save(format='binary', folder = data_folder / f'{probe_name}_{epoch_name_to_shank[epoch_name]}_lfp_nocmr', overwrite=True, chunk_duration='30s')

#sort = si.run_sorter('kilosort4', rec, folder= data_folder / f'{probe_name}_{epoch_name_to_shank[epoch_name]}_kilosort', do_correction=False, use_binary_file=False, remove_existing_folder=False, verbose=True)

sort = si.load(data_folder / f'{probe_name}_{epoch_name_to_shank[epoch_name]}_kilosort')

pp_rec = si.bandpass_filter(si.common_reference(rec)).save(format='binary', folder=f'temp/temp_recording_{probe_name}_{epoch_name_to_shank[epoch_name]}', overwrite=True)

analyzer = si.create_sorting_analyzer(
    sorting=sort,
    recording = pp_rec,
    folder= data_folder / f'{probe_name}_{epoch_name_to_shank[epoch_name]}_analyzer',
    format='binary_folder',
    sparsity_kwargs = {'radius_um' : 70},
    overwrite=True,
)

analyzer.compute(['random_spikes', 'noise_levels', 'waveforms', 'templates', 'unit_locations', 'spike_amplitudes', 'spike_locations', 'quality_metrics', 'template_metrics'])

unit_quality = si.bombcell_label_units(analyzer)
analyzer.set_sorting_property(key='bombcell', values = unit_quality['bombcell_label'].values.astype(str))
