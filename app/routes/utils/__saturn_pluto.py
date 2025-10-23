
# --------------------------------------
# THIS DOWNLOADED 1900 2050 SUCCESSFULLY
# --------------------------------------
# import swisseph as swe
# import pandas as pd
# import numpy as np
# import datetime
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

# # Define date range
# start_date = datetime.date(1900, 1, 1)
# end_date = datetime.date(1950, 12, 31)
# delta = datetime.timedelta(weeks=1)  # Weekly intervals

# dates = []
# mars_longitudes = []
# saturn_longitudes = []
# pluto_longitudes = []

# # Compute planetary longitudes weekly
# current_date = start_date
# while current_date <= end_date:
#     jd = swe.julday(current_date.year, current_date.month, current_date.day)
#     mars_longitudes.append(swe.calc_ut(jd, swe.MARS)[0][0])
#     saturn_longitudes.append(swe.calc_ut(jd, swe.SATURN)[0][0])
#     pluto_longitudes.append(swe.calc_ut(jd, swe.PLUTO)[0][0])
#     dates.append(current_date)
#     current_date += delta

# # Convert to DataFrame
# df = pd.DataFrame({
#     "Date": dates,
#     "Mars Longitude": mars_longitudes,
#     "Saturn Longitude": saturn_longitudes,
#     "Pluto Longitude": pluto_longitudes
# })

# # Compute angular separations
# df["Mars-Saturn Angle"] = np.abs(df["Mars Longitude"] - df["Saturn Longitude"]) % 360
# df["Mars-Pluto Angle"] = np.abs(df["Mars Longitude"] - df["Pluto Longitude"]) % 360
# df["Saturn-Pluto Angle"] = np.abs(df["Saturn Longitude"] - df["Pluto Longitude"]) % 360

# # Define aspect detection with ±5° orb
# orb = 5
# df["Saturn-Pluto Square"] = df["Saturn-Pluto Angle"].between(90 - orb, 90 + orb) | df["Saturn-Pluto Angle"].between(270 - orb, 270 + orb)
# df["Saturn-Pluto Opposition"] = df["Saturn-Pluto Angle"].between(180 - orb, 180 + orb)
# df["Mars-Pluto Square"] = df["Mars-Pluto Angle"].between(90 - orb, 90 + orb) | df["Mars-Pluto Angle"].between(270 - orb, 270 + orb)
# df["Mars-Pluto Opposition"] = df["Mars-Pluto Angle"].between(180 - orb, 180 + orb)
# df["Mars-Saturn Square"] = df["Mars-Saturn Angle"].between(90 - orb, 90 + orb) | df["Mars-Saturn Angle"].between(270 - orb, 270 + orb)
# df["Mars-Saturn Opposition"] = df["Mars-Saturn Angle"].between(180 - orb, 180 + orb)

# # Save dataset to CSV
# df.to_csv("mars_saturn_pluto_aspects_1900_1950.csv", index=False)

# # Extract aspect start & end dates
# aspect_events = []
# for aspect in ["Saturn-Pluto Square", "Saturn-Pluto Opposition", "Mars-Pluto Square", "Mars-Pluto Opposition", "Mars-Saturn Square", "Mars-Saturn Opposition"]:
#     aspect_data = df[df[aspect]].copy()
#     if not aspect_data.empty:
#         aspect_events.append({
#             "Aspect": aspect,
#             "Start Date": aspect_data.iloc[0]["Date"],
#             "End Date": aspect_data.iloc[-1]["Date"],
#             "Duration (Weeks)": len(aspect_data)
#         })

# aspect_df = pd.DataFrame(aspect_events)
# aspect_df.to_csv("aspect_durations_1900_1950.csv", index=False)


# --------------------------------------
# THIS VISUALIZAES SPECIFIC ASPECTS
# --------------------------------------

# import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

# def plot_aspects_period(start_year, end_year, data_file):
#     # Read data
#     df = pd.read_csv(data_file)
#     df['Date'] = pd.to_datetime(df['Date'])
    
#     # Filter for selected period
#     mask = (df['Date'].dt.year >= start_year) & (df['Date'].dt.year <= end_year)
#     period_df = df[mask]
    
#     # Aspects to plot
#     aspects = [
#         'Saturn-Pluto Square', 
#         'Saturn-Pluto Opposition',
#         'Mars-Pluto Square', 
#         'Mars-Pluto Opposition',
#         'Mars-Saturn Square', 
#         'Mars-Saturn Opposition'
#     ]
    
#     # Colors for each planetary pair
#     colors = {
#         'Saturn-Pluto': 'purple',
#         'Mars-Pluto': 'red',
#         'Mars-Saturn': 'green'
#     }
    
#     # Create plot
#     fig, ax = plt.subplots(figsize=(15, 8))
    
#     # Plot each aspect
#     for i, aspect in enumerate(aspects):
#         # Get dates where aspect is True
#         aspect_dates = period_df[period_df[aspect]]['Date']
        
#         # Get base color for the aspect
#         base_pair = aspect.split(' ')[0]
#         color = colors[base_pair]
        
#         # Plot points
#         ax.scatter(aspect_dates, [i] * len(aspect_dates), 
#                   c=color, alpha=0.7, s=50)
    
#     # Customize plot
#     ax.set_yticks(range(len(aspects)))
#     ax.set_yticklabels(aspects)
#     ax.grid(True, alpha=0.3)
    
#     # Format x-axis
#     ax.xaxis.set_major_locator(mdates.YearLocator())
#     ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
#     plt.xticks(rotation=45)
    
#     plt.title(f'Planetary Aspects ({start_year}-{end_year})')
#     plt.tight_layout()
    
#     # Print detailed data below
#     print(f"\nDetailed aspect data for {start_year}-{end_year}:")
#     for aspect in aspects:
#         aspect_data = period_df[period_df[aspect]]
#         if len(aspect_data) > 0:
#             print(f"\n{aspect}:")
#             for _, row in aspect_data.iterrows():
#                 angle_column = f"{aspect.split(' ')[0]} Angle"
#                 print(f"{row['Date'].strftime('%Y-%m-%d')}: {row[angle_column]:.1f}°")
    
#     plt.show()

# # Usage example:
# start_year = 1939
# end_year = 1940
# plot_aspects_period(start_year, end_year, '/Users/federico/Desktop/Hermetic Library/monsieur_neo/mars_saturn_pluto_aspects_1900_2050.csv')


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_aspects_period(start_year, end_year, data_file):
    # Read data
    df = pd.read_csv(data_file)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter for selected period
    mask = (df['Date'].dt.year >= start_year) & (df['Date'].dt.year <= end_year)
    period_df = df[mask]
    
    # Aspects to plot
    aspects = [
        'Saturn-Pluto Square', 
        'Saturn-Pluto Opposition',
        'Mars-Pluto Square', 
        'Mars-Pluto Opposition',
        'Mars-Saturn Square', 
        'Mars-Saturn Opposition'
    ]
    
    # Colors for each aspect
    colors = {
        'Saturn-Pluto Square': 'purple',
        'Saturn-Pluto Opposition': 'pink',
        'Mars-Pluto Square': 'orange',
        'Mars-Pluto Opposition': 'red',
        'Mars-Saturn Square': 'green',
        'Mars-Saturn Opposition': 'blue'
    }
    
    # Mapping aspects to correct angle column
    angle_mapping = {
        'Saturn-Pluto Square': 'Saturn-Pluto Angle',
        'Saturn-Pluto Opposition': 'Saturn-Pluto Angle',
        'Mars-Pluto Square': 'Mars-Pluto Angle',
        'Mars-Pluto Opposition': 'Mars-Pluto Angle',
        'Mars-Saturn Square': 'Mars-Saturn Angle',
        'Mars-Saturn Opposition': 'Mars-Saturn Angle'
    }
    
    # Create plot
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Plot each aspect
    for i, aspect in enumerate(aspects):
        # Get dates where aspect is True
        aspect_dates = period_df[period_df[aspect]]['Date']
        
        # Get corresponding angle column
        angle_col = angle_mapping[aspect]
        
        # Plot points
        ax.scatter(aspect_dates, [i] * len(aspect_dates), 
                   c=colors[aspect], alpha=0.7, s=50, label=aspect if i == 0 else "")
    
    # Customize plot
    ax.set_yticks(range(len(aspects)))
    ax.set_yticklabels(aspects)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis with months and years
    ax.xaxis.set_major_locator(mdates.YearLocator())  # Major ticks = Years
    ax.xaxis.set_minor_locator(mdates.MonthLocator())  # Minor ticks = Months
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # Year format
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b'))  # Month format
    
    plt.xticks(rotation=45)  # Rotate labels for better visibility
    
    plt.title(f'Planetary Aspects ({start_year}-{end_year})')
    plt.tight_layout()
    
    # Print detailed data below
    print(f"\nDetailed aspect data for {start_year}-{end_year}:")
    for aspect in aspects:
        aspect_data = period_df[period_df[aspect]]
        if not aspect_data.empty:
            angle_col = angle_mapping[aspect]
            print(f"\n{aspect}:")
            for _, row in aspect_data.iterrows():
                print(f"{row['Date'].strftime('%Y-%m-%d')}: {row[angle_col]:.1f}°")
    
    plt.show()

# Usage example:
start_year = 1939
end_year = 1940
plot_aspects_period(start_year, end_year, "/Users/federico/Desktop/Hermetic Library/monsieur_neo/mars_saturn_pluto_aspects_1900_2050.csv")
