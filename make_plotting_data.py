from pathlib import Path
import spikeinterface.full as si
import pandas as pd
import numpy as np
import pynapple as nap
from .config import epoch_name_to_shank, probe_names

si.set_global_job_kwargs(n_jobs=4)

for probe_name in probe_names:

    data_folder = Path(f'processed/{probe_name}')

    for epoch_name, probe_place in epoch_name_to_shank:

        # analyzer stuff

        analyzer = si.load_sorting_analyzer(data_folder / f'{probe_name}_{epoch_name_to_shank[epoch_name]}_analyzer')

        unit_quality = si.bombcell_label_units(analyzer)

        unit_locations = analyzer.get_extension('unit_locations').get_data()[:,1]
        unit_locations_x = analyzer.get_extension('unit_locations').get_data()[:,0]

        unit_quality['depth'] = unit_locations
        unit_quality['x'] = unit_locations_x

        unit_quality.to_csv(data_folder / f'{probe_name}_{probe_place}_quality.csv')

        noise_levels = analyzer.get_extension('noise_levels').get_data()
        channel_locations = analyzer.get_channel_locations()[:,1]
        pd.DataFrame(data=np.array([noise_levels, channel_locations]).T, columns=['noise_levels', 'depth']).to_csv(data_folder / f'{probe_name}_{probe_place}_noise.csv')

        # lfp stuff
        lfp_rec = si.load(data_folder / f'{probe_name}_{probe_place}_lfp')

        samples = lfp_rec.get_num_samples()
        Fs = 600
        t = np.arange(0,samples)/Fs

        data = []
        for channel_index in range(lfp_rec.get_num_channels()):

            d = lfp_rec.get_traces(channel_ids=[lfp_rec.channel_ids[channel_index]]).T[0]

            channel_depth = lfp_rec.get_channel_locations()[channel_index][1]

            channel_lfp = nap.Tsd(t=t, d=d)

            psd = nap.compute_power_spectral_density(channel_lfp, fs=Fs)

            dt = psd.index[1] - psd.index[0]

            total_delta_power = np.sum(psd[(psd.index > 0.5) & (psd.index < 4)].values)*dt
            total_theta_power = np.sum(psd[(psd.index > 6) & (psd.index < 12)].values)*dt
            total_slow_gamma_power = np.sum(psd[(psd.index > 30) & (psd.index < 50)].values)*dt
            total_mid_gamma_power = np.sum(psd[(psd.index > 50) & (psd.index < 90)].values)*dt
            total_fast_gamma_power = np.sum(psd[(psd.index > 90) & (psd.index < 150)].values)*dt
            total_ripple_power = np.sum(psd[(psd.index > 150) & (psd.index < 250)].values)*dt

            data.append([channel_depth, total_delta_power, total_theta_power, total_slow_gamma_power, total_mid_gamma_power, total_fast_gamma_power, total_ripple_power])

        powers = pd.DataFrame(data, columns = ['depth', 'delta_power', 'theta_power', 'slow_gamma_power', 'mid_gamma_power', 'fast_gamma_power', 'ripple_power'])
        powers.to_csv(data_folder / f'{probe_name}_{probe_place}_powers.csv')
