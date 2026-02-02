import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.patches as mpatches

def plot_quakes():
    csv_file = "china_quakes.csv"
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        return

    if df.empty:
        print("No earthquake data to plot.")
        return

    print(f"Plotting {len(df)} earthquakes...")

    # Create figure and axis with Cartopy projection
    fig = plt.figure(figsize=(12, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Set map extent (China mainland roughly)
    ax.set_extent([73, 135, 18, 54], crs=ccrs.PlateCarree())

    # Add map features
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.RIVERS, alpha=0.5)

    # Plot earthquakes
    # Magnitude -> Circle size (s)
    # Depth -> Color (c)
    
    # Scale magnitude for better visibility
    sizes = (df['magnitude'] - 4.0) * 100
    
    scatter = ax.scatter(
        df['longitude'], df['latitude'],
        s=sizes,
        c=df['depth_km'],
        cmap='plasma_r', # plasma_r: shallow is bright/warm, deep is cool
        alpha=0.7,
        edgecolors='black',
        linewidth=0.5,
        transform=ccrs.PlateCarree(),
        label='Earthquakes'
    )

    # Add colorbar for depth
    cbar = plt.colorbar(scatter, ax=ax, orientation='vertical', pad=0.02, aspect=30)
    cbar.set_label('Depth (km)')

    # Add legend for magnitude
    # Create proxy artists for the magnitude legend
    mag_levels = [4.5, 5.0, 5.5, 6.0]
    legend_elements = [
        plt.scatter([], [], s=(m - 4.0) * 100, c='gray', alpha=0.6, edgecolors='black', label=f'M {m}')
        for m in mag_levels
    ]
    ax.legend(handles=legend_elements, title="Magnitude", loc='lower left', scatterpoints=1)

    plt.title('Earthquake Distribution in Mainland China (2015-2025)\nMagnitude 4.5-6, Depth 0-5km', fontsize=14)
    
    # Add gridlines
    gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    gl.top_labels = False
    gl.right_labels = False

    output_file = "china_quakes_map.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Map saved to {output_file}")
    plt.close()

if __name__ == "__main__":
    plot_quakes()
