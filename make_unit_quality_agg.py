import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from config import epoch_name_to_shank, probe_names

def plot_probe_property(
    property_name='good', 
    probe_name=None,
    color='#2ca02c', 
    xlabel='Power (a.u.)'
):
    """
    Plots a 2x4 grid:
      - Columns 0-3: Shank 1 to Shank 4
      - Row 0: Top bank
      - Row 1: Bottom bank
    """
    
    file_pattern=f'processed/{probe_name}/{probe_name}_{{shank}}_quality.csv'
    
    shanks = ['s1', 's2', 's3', 's4']
    banks = ['top', 'bot']  # row 0 = top, row 1 = bottom
    
    dfs = []

    for row_idx, bank in enumerate(banks):
        for col_idx, s in enumerate(shanks):
            
            shank_key = f"{s}{bank}"
            
            filename = file_pattern.format(shank=shank_key)
            dfs.append(pd.read_csv(filename))
    
    big_df = pd.concat(dfs)
    good_df = big_df.query(f'bombcell_label == "{property_name}"')

    fig, ax = plt.subplots(figsize=(6, 8))
    ax.scatter(good_df['x'], good_df['depth'], c=color, s=30)

    step = 720
    y_min, y_max = good_df['depth'].min(), good_df['depth'].max()
    multiples = np.arange(np.floor(y_min / step) * step, y_max + step, step)
    for y in multiples:
        plt.axhline(y=y, color='gray', linestyle='--', linewidth=0.8, alpha=0.4, zorder=1)


    ax.set_xlabel('x (µm)')
    ax.set_ylabel('Depth (µm)')
    ax.set_title(f'{property_name} Unit Positions')

    return fig
    
    #fig.suptitle(f"{probe_name}: {property_name.replace('_', ' ').title()}", fontsize=13, fontweight='bold', y=0.99)
    #fig.tight_layout()
    #return fig





for probe_name in ['ProbeA', 'ProbeB']:
    for property_name in ['good', 'mua']:
        if property_name == 'good':
            color = 'green'
        if property_name == 'mua':
            color = 'blue'

        fig = plot_probe_property(property_name=property_name, probe_name=probe_name, color=color)
        fig.savefig(f'plots/{probe_name}/{probe_name}_{property_name}_units.png')



