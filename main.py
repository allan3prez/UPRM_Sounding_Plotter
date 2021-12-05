# Script developed by Allan Cruz for use with radiosonde Skysonde data gathered on UPRM with MetPy Tutorial
from scipy.signal import medfilt
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import pandas as pd
import numpy as np
import metpy.calc as mpcalc
from metpy.plots import Hodograph, SkewT
from metpy.units import units


# changes the object into shorter useful variables with units
def data_to_variables(data):
    p = data['pressure'].values * units.hPa
    T = data['temperature'].values * units.degC
    RH = data['Humidity(RH%)'].values / 100
    alt = data['height'].values * units.km
    wind_speed = data['speed'].values * units.meters / units.second
    wind_dir = data['direction'].values * units.degree
    return p, T, RH, alt, wind_speed, wind_dir

# finds the index when pressure increases (radiosonde starts to drop)
def first_increasing_index(press):
    i = 1
    while press[i] < press[i - 1]:
        i += 1
    return i

# intervals of pressure to place wind barbs on
def pressure_interval(p, u, v, upper=100, lower=1000, spacing=25):
    intervals = list(range(upper, lower, spacing))

    ix = []
    for center in intervals:
        index = (np.abs(p - center)).argmin()
        if index not in ix:
            ix.append(index)

    return p[ix], u[ix], v[ix]

if __name__=='__main__':

    # read data
    # filenumber and date for plot title
    filenumber = ""
    date = "MM/DD/YYYY"
    # input file path here
    file_path = f'D:/Documents/Radiosonde_project/uprm033/uprm033.csv'


    #name columns
    columns = ['height', 'pressure', 'temperature', 'Humidity(RH%)', 'direction', 'speed']
    df = pd.read_csv(file_path, skiprows=105, names=columns, usecols=[5, 6, 7, 9, 34, 33], na_values='99999')


    #filtering
    #remove flag values
    df = df.dropna(how='any').reset_index(drop=True)
    #remove duplicate values
    df = df.drop_duplicates(subset='pressure', keep='first')

    # changes the object into shorter useful variables with units
    p, T, RH, alt, wind_speed, wind_dir = data_to_variables(df)
    # calculate dew point
    T_DP = mpcalc.dewpoint_from_relative_humidity(T, RH)
    # calculate wind vectors
    u, v = mpcalc.wind_components(wind_speed, wind_dir)
    # calculate the LCL
    lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], T_DP[0])


    #keep only every nth row to reduce data points for plotting
    rows_to_skip = 5
    df = df.iloc[::rows_to_skip,:]
    p, T, RH, alt, wind_speed, wind_dir = data_to_variables(df)

    # resize all arrays to match pressure fix
    highest_p = first_increasing_index(p)
    p = p[2:highest_p]
    T = T[2:highest_p]
    T_DP = T_DP[2:highest_p]
    RH = RH[2:highest_p]
    alt = alt[2:highest_p]
    v = v[2:highest_p]
    u = u[2:highest_p]

    # calculate parcel profile
    parcel_prof = mpcalc.parcel_profile(p, T[0], T_DP[0]).to('degC')
    # calculate CAPE and CIN
    CAPE, CIN, = mpcalc.cape_cin(p, T, T_DP, parcel_prof)
    # set barb plotting interval
    p_,u,v = pressure_interval(p.magnitude,u,v)
    # wanted mixing ratios
    w = np.array([0.028, 0.024, 0.020, 0.016, 0.012, 0.008, 0.004]).reshape(-1, 1) * units('g/g')
    __p = units.hPa * np.linspace(1000, 600, 7)

    # new figure
    fig = plt.figure(figsize=(10, 5))
    gs = gridspec.GridSpec(1, 2)
    skew = SkewT(fig, rotation=45, subplot=gs[:, :1])
    skew.ax.set_ylim(1000, 50)
    skew.ax.set_xlim(-60, 40)

    # plot data

    for val in w.flatten()[::3]:
        dewpt = mpcalc.dewpoint(mpcalc.vapor_pressure(1250 * units.hPa, val))
        skew.ax.text(dewpt, 1230, str(val.to('g/kg').m), horizontalalignment='center', verticalalignment='center', color='green')

    skew.plot(p, T, 'r', linewidth=2, markersize=8)
    skew.plot(p, T_DP, 'b', linewidth=2)
    skew.plot_barbs(p_, u, v, y_clip_radius=0.2)
    skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')
    skew.plot(p, parcel_prof, 'k', linewidth=2)
    skew.shade_cin(p, T, parcel_prof, T_DP)
    skew.shade_cape(p, T, parcel_prof)
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines(w, __p)

    # labels
    fig.suptitle(f"UPRM Sounding #{filenumber} on {date}", fontsize=16)
    Values_to_print = f" LCL: {lcl_temperature.magnitude.round(3)} {lcl_temperature.units}, {lcl_pressure.magnitude.round(3)}" \
                      f" {lcl_pressure.units} \n" \
                      f"CAPE: {CAPE.magnitude.round(3)} {CAPE.units} \n" \
                      f" CIN: {CIN.magnitude.round(3)} {CIN.units}"

    fig.text(0.5, 0.8, Values_to_print)


    plt.show()