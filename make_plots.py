from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from .config import epoch_name_to_shank, probe_names

for probe_name in probe_names:

    data_folder = Path(f'processed/{probe_name}')

    for epoch_name, probe_place in epoch_name_to_shank:

        for epoch_name, probe_place in epoch_name_to_shank:

            powers = pd.read_csv(data_folder / f"{probe_name}_{probe_place}_powers.csv").sort_values("depth")

            noise_df = pd.read_csv(data_folder / f"{probe_name}_{probe_place}_noise.csv").sort_values("depth")
            noise_mean = (
                noise_df.groupby("depth", as_index=False)["noise_levels"]
                .mean()
                .sort_values("depth")
            )

            # 3. Load quality data and exclude noise units
            quality_df = pd.read_csv(data_folder / f"{probe_name}_{probe_place}_quality.csv")
            units_df = quality_df[quality_df["bombcell_label"] != "noise"].copy()

            # Configure 1x6 subplot layout
            fig, axes = plt.subplots(
                1,
                9,
                figsize=(20, 6),
                sharey=True,
            )

            # --- Subplots 1–4: LFP Power Bands ---
            power_bands = [
                ("delta_power", "Delta Power", "C0"),
                ("theta_power", "Theta Power", "C1"),
                ("slow_gamma_power", "Slow Gamma", "C2"),
                ("mid_gamma_power", "Mid Gamma", "C3"),
                ("fast_gamma_power", "Fast Gamma", "C4"),
                ("ripple_power", "Ripple Power", "C5"),
            ]

            for ax, (col, title, color) in zip(axes[:6], power_bands):
                ax.plot(powers[col], powers["depth"], color=color)
                ax.set_title(title, fontsize=10, fontweight="bold")
                ax.set_xlabel("Power")

            ax_noise = axes[6]
            ax_noise.plot(
                noise_mean["noise_levels"],
                noise_mean["depth"],
                lw=1.5,
            )
            ax_noise.set_title("Neural Noise", fontsize=10, fontweight="bold")
            ax_noise.set_xlabel("Noise Level (µV)", fontsize=9)

            # --- Subplot 6: Bombcell Units Scatter ---
            ax_units = axes[7]
            categories = ["mua", "non_soma", "good"]
            colors = {
                "mua": "#1f77b4",  # Blue
                "non_soma": "#ff7f0e",  # Orange
                "good": "#2ca02c",  # Green
            }
            alphas = {
                "mua": 0.5,
                "non_soma": 0.5,
                "good": 1,
            }

            if len(units_df) != 0:

                for i, cat in enumerate(categories):
                    sub = units_df[units_df["bombcell_label"] == cat]
                    ax_units.scatter(
                        sub["x"],
                        sub["depth"],
                        c=colors[cat],
                        label=f"{cat} (n={len(sub)})",
                        alpha=alphas[cat],
                        s=28,
                        edgecolors="none",
                    )

            
            ax_units.set_xlim(np.nanmin(units_df["x"])-100, np.nanmax(units_df["x"])+100)
            ax_units.legend(loc="lower right", fontsize=8, framealpha=0.85)
                
            ax_units.set_title("Bombcell Units", fontsize=10, fontweight="bold")
            axes[0].set_ylabel("Depth (µm)", fontsize=11)

            # --- Subplot 7: Unit Depth Distribution (200 µm Bins) ---
            ax_dist = axes[8]
            bins_200um = np.arange(min(noise_df['depth'])-100, max(noise_df['depth'])+100 , 200)
            ax_dist.hist(
                units_df["depth"],
                bins=bins_200um,
                orientation="horizontal",
                alpha=0.85,
            )
            ax_dist.set_title("Unit Count", fontsize=10, fontweight="bold")
            ax_dist.set_xlabel("Count", fontsize=9)
            
            ax_dist.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=4))

            # --- Global formatting ---
            for ax in axes:
                # Set ~4 horizontal grid lines along the shared depth axis
                ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=4))
                ax.grid(axis="y", linestyle="--", alpha=0.6)
                ax.set_ylim(min(noise_df['depth'])-150, max(noise_df['depth'])+150)

            # Optional: Invert y-axis if surface is dorsal (depth = 0 µm at top)
            # axes[0].invert_yaxis()

            fig.suptitle(f'{probe_name}  -  shank {probe_place[1]}  -  {probe_place[2:]}')

            fig.tight_layout()

            fig.savefig(data_folder / f'../../plots/{probe_name}/{probe_name}_{probe_place}_summary.png')
