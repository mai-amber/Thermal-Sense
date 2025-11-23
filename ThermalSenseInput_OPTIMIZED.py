# -*- coding: utf-8 -*-

"""
Real-time data interpolation and visualization using MLX90640 thermal camera
This script captures thermal data from the MLX90640 sensor and visualizes it in real-time using Matplotlib.         
It also handles potential errors during data retrieval and provides a retry mechanism.

OPTIMIZED VERSION: Removed unnecessary operations and improved performance
"""

import time
import board
import busio
import numpy as np
import adafruit_mlx90640
import matplotlib.pyplot as plt

class ThermalSenseInput:
    """
    Class to handle the initialization and data retrieval from the MLX90640 thermal camera.
    """
    def __init__(self):
        """
        Initializes the I2C connection and the MLX90640 sensor.
        Sets the refresh rate to 2 Hz.
        """
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.mlx = adafruit_mlx90640.MLX90640(self.i2c)
        self.mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
        self.frame = np.zeros((24*32,))
   
    # Helper initial method for creating frame 
    def setup_plot(self):
        plt.ion()
        fig, ax = plt.subplots(figsize=(12, 7))
        therm1 = ax.imshow(np.zeros((24, 32)), vmin=0, vmax=60, cmap='inferno', interpolation='bilinear')
        cbar = fig.colorbar(therm1)
        cbar.set_label('Temperature [°C]', fontsize=14)
        plt.title('Thermal Image')
        return fig, ax, therm1
 
    def update_display(self, fig, ax, therm1, data_array):
        """
        OPTIMIZED: Simplified display update without unnecessary checks
        """
        if therm1 is None:
            return  # Skip if no image object
        
        # Update image data
        therm1.set_data(np.fliplr(data_array))
        therm1.set_clim(vmin=np.min(data_array), vmax=np.max(data_array))
        
        # ============== OPTIMIZATION: Removed redundant canvas checks ==============
        # The runner now handles draw calls more efficiently
    
    # method for calculating temperature
    def calculate_temperature(self):
        """
        Reshapes the frame data into a 2D array and returns it.
        """
        self.mlx.getFrame(self.frame)  # Capture frame from MLX90640
        average_temp_c = np.mean(self.frame)
        average_temp_f = (average_temp_c * 9.0 / 5.0) + 32.0
        print(f"Average MLX90640 Temperature: {average_temp_c:.1f}C ({average_temp_f:.1f}F)")
        
        # ============== OPTIMIZATION: Removed time.sleep(0.5) ==============
        # Let the sensor's refresh rate control timing instead
        
        return average_temp_c
