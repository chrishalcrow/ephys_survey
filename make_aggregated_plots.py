import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from config import epoch_name_to_shank, probe_names

def plot_probe_property(
    property_name='gamma_power', 
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
    
    file_pattern=f'processed/{probe_name}/{probe_name}_{{shank}}_powers.csv'
    
    # 2 rows x 4 columns; sharey='row' maintains consistent depth scaling per bank
    fig, axes = plt.subplots(
        2, 4, 
        figsize=(14, 8), 
        sharey='row', 
        sharex=True
    )
    
    shanks = ['s1', 's2', 's3', 's4']
    banks = ['top', 'bot']  # row 0 = top, row 1 = bottom

    for row_idx, bank in enumerate(banks):
        for col_idx, s in enumerate(shanks):
            
            shank_key = f"{s}{bank}"
            ax = axes[row_idx, col_idx]
            
            filename = file_pattern.format(shank=shank_key)
            df = pd.read_csv(filename).sort_values('depth')
            ax.semilogx(df[property_name], df['depth'], color=color, lw=1.4)
            
            # Subplot titles only on the top row, column labels for clarity
            if row_idx == 0:
                ax.set_title(f"Shank {col_idx + 1}\n(Top Bank)")
            else:
                ax.set_title(f"Shank {col_idx + 1} (Bottom Bank)")
            
            # X-axis label only on bottom row to avoid clutter
            if row_idx == 1:
                ax.set_xlabel(f'{property_name} (log)', fontsize=10)
                
            # 4 horizontal depth reference grid lines
            step = 720
            multiples = np.arange(np.min(df['depth']), np.max(df['depth']), step)
            for y in multiples:
                ax.axhline(y=y, color='gray', linestyle='--', linewidth=0.8, alpha=0.4, zorder=1)            
        
    fig.suptitle(f"{probe_name}: {property_name.replace('_', ' ').title()}", fontsize=13, fontweight='bold', y=0.99)
    fig.tight_layout()
    return fig

power_bands = {
    "delta_power": "C0",
    "theta_power": "C1",
    "slow_gamma_power": "C2",
    "mid_gamma_power": "C3",
    "fast_gamma_power": "C4",
    "ripple_power": "C5",
}

for probe_name in ['ProbeA', 'ProbeB']:
    for power_name, plot_color in power_bands.items():
        fig = plot_probe_property(power_name, probe_name = probe_name, color=plot_color)
        fig.savefig(f'plots/{probe_name}/{probe_name}_agg_{power_name}.png')
