from pathlib import Path
import spikeinterface.full as si
import probeinterface as pi
from aeon.dj_pipeline.utils.spike_sorting_utils import read_bonsai_onix_arrow

from .config import experiment_path, epoch_name_to_shank, probe_names

si.set_global_job_kwargs(n_jobs=4)

for probe_name in probe_names:

    data_folder = Path(f'processed/{probe_name}')

    for epoch_name, probe_place in epoch_name_to_shank:

        epoch_path = experiment_path / f'{epoch_name}/NeuropixelsV2'

        ephys_path = epoch_path / f'NeuropixelsV2_{probe_name}_0.arrow'
        probe_path = list(epoch_path.glob('*.json'))[0]

        rec = si.unsigned_to_signed(read_bonsai_onix_arrow(str(ephys_path), sampling_frequency=30_000))

        probe = pi.read_probeinterface(probe_path)
        rec.set_probegroup(probe)

        # make LFP recording
        half_rec = rec.select_channels(rec.channel_ids[rec.get_channel_locations()[:,0] == rec.get_channel_locations()[0][0]])
        lfp_rec = si.decimate(si.bandpass_filter(si.common_reference(half_rec), freq_min=0.5, freq_max = 300, ignore_low_freq_error=True, margin_ms=12_000), decimation_factor=50)
        lfp_rec.save(format='binary', folder = data_folder / f'{probe_name}_{epoch_name_to_shank[epoch_name]}_lfp', overwrite=True, chunk_duration='30s')

        sort = si.run_sorter('kilosort4', rec, folder= data_folder / f'{probe_name}_{epoch_name_to_shank[epoch_name]}_kilosort', do_correction=False, use_binary_file=False, remove_existing_folder=True, verbose=True)

        pp_rec = si.bandpass_filter(si.common_reference(rec)).save(format='binary', folder='temp_recording', overwrite=True)

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
