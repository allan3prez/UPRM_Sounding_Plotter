# Abstract
Radiosondes are a useful method of taking measurements in the higher-level atmosphere to help in the forecasting process. The data of these soundings must be pre-processed and visualized to be useful for analysis and forecasting. In this project we developed a script to pre-process, filter, and visualize radiosonde data collected from Mayagüez, Puerto Rico with the SkySonde software and MetPy library. The data proofed useful in showing the state of the atmosphere at higher levels and the effects of rain from low clouds in the higher atmosphere. The quick results of the scripting for the processing of data allowed more time to be used while analyzing the visualizations.

# Requirements
- installed Metpy package with all it includes
- radio sounding csv data from skysonde client (other software might change the column arrangement)

# How to Plot
Example provided file is used
1. Change the file_path variable to the file you want to use in line 49. Make sure to replace '\' to '/' and include the '.csv'
2. Add filenumber and date for the title of the plot.
3. To change the plot title change the input string on line 122.
4. To increase or reduce plot point resolution change the amount of rows_to_skip on line 74.

# Planed additions
- Provide the option to either skip rows or use average of rows.
- Addition of more calculations for analysis
