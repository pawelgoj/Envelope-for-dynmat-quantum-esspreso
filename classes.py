# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 23:16:18 2021

@author: pagoj
"""
from logging import raiseExceptions
import math as math
from typing import Tuple
import scipy.special as special
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt

#Plots the strand positions calculated from QE on the graph
def int_bonds(x, y, intensity):
    y = np.zeros(len(y))
    j = 0
    
    for i in range(0, len(x) -2):
        if j > (len(intensity) -1):
            break
        else:
            if (x[i] <= intensity[j][0]) and (intensity[j][0] <= x[i+1]): 
                while intensity[j][0] <= x[i+1]:
                    y[i] = y[i] + np.array(intensity[j][1])
                    j +=1
                    if j > (len(intensity) -1):
                        break
            else:
                y[i] = 0
    
    return y

class Dane:
    """Class dane, objects are data read from a dynmat or txt file.
    """
    def __init__(self, name_of_file: str, start_data_read_in_line: str):
       self.name_of_file = name_of_file
       self.start_data_read_in_line = start_data_read_in_line
    def wczytaj(self) -> list:
       """Loads a file and returns a list of mods 

       Returns:
           list: List of mods 
       """
       try:  
           file = open(self.name_of_file, "r")
       except: 
           print("There is no such file!!!")
           
       line = ""
       if self.start_data_read_in_line != "":
           while self.start_data_read_in_line not in line: 
               line = file.readline()
           
       list_of_mods =[]
       line = file.readline()
       if self.start_data_read_in_line == "":
           line = file.readline()
       while not ("" == line or "\n" == line) :
           splited = line.split()
           mod = []
           for x in splited: 
               mod.append(float(x))
           list_of_mods.append(mod)
           line = file.readline()  
       file.close()
       return list_of_mods  

class ListOfMods:
    """The object is the mods tables from loaded files
    """
    def __init__(self, list_of_mods: list):
        self.list_of_mods = list_of_mods
    def max_min(self) -> tuple:
        """Return max and min wavenumber from list of mods 

        Returns:
            tuple: min, max
        """
        if len(self.list_of_mods[0]) == 3:
            i = 0
        else:
            i = 1
        minOf = math.ceil(self.list_of_mods[0][i] - 5)
        lenght = len(self.list_of_mods) - 1
        maxOf = math.ceil(self.list_of_mods[lenght][i] + 100)
        return minOf, maxOf
    def raman(self) -> list:
        """Return list of raman mods.

        Returns:
            list: list of Raman mods 
        """
        if len(self.list_of_mods[0]) == 3:
            x1, x2, x3 = zip(*self.list_of_mods)
            raman = list(zip(x1, x3))
            del x1 
            del x2
            del x3 
        else:
            x1, x2, x3, x4, x5, x6 = zip(*self.list_of_mods)
            raman = list(zip(x2, x5))
            del x1
            del x2
            del x3 
            del x4
            del x5
            del x6
        return raman

    def ir(self) -> list:
        """Return list of ir mods.

        Returns:
            list: list of ir mods 
        """
        if len(self.list_of_mods[0]) == 3:
            x1, x2, x3 = zip(*self.list_of_mods)
            ir = list(zip(x1, x2))
            del x1 
            del x2
            del x3 
        else:
            x1, x2, x3, x4, x5, x6 = zip(*self.list_of_mods)
            ir = list(zip(x2, x4))
            del x1
            del x2
            del x3 
            del x4
            del x5
            del x6
        return ir

class Pasmo:
    """Objects are a single band.
    """
    def __init__(self, Intensity: float, wavenumber: float, number_of_points: int, minimum: float, maximum: float):
        self.Intensity = Intensity
        self.wavenumber = wavenumber
        self.number_of_points = number_of_points
        self.maximum = maximum
        self.minimum = minimum

    def voigtcurve(self, Q1, Q2) -> np.array:
        """Return a voigt curve  for band
        This mathod is the fastes. 
        Returns:
            np.array: voigt curve  for band
        """
        delta = (self.maximum - self.minimum)/self.number_of_points
        x = self.minimum
        curve = np.zeros((2,self.number_of_points))
        voigtMax = special.voigt_profile(0, Q1, Q2)
        scale = 1 / voigtMax
        for i in range(1, self.number_of_points):
            curve[1, i] = round(self.Intensity * scale * special.voigt_profile(x - self.wavenumber, Q1, Q2), 4)
            curve[0, i] = x
            x += delta
        return curve       
 
class Envelope:
    """objects are lists of bands for Raman or Ir"""
    def __init__(self, curve: list, NrPoints: int, minimum: float, maximum: float):
        self.curve = curve
        self.NrPoints = NrPoints
        self.minimum = minimum
        self.maximum = maximum
    def do_envelope(self, typeBand: str, Q1: float, Q2: float = 0) -> np.array:
        """Returns an envelope

        Args:
            typeBand (str): Gauss/Cauchy/Voigt 
            Q2 (float): Q2 for Voigt curve 

        Returns:
            np.array: envelope 
        """
        wyniki = np.zeros((2,self.NrPoints))
        if typeBand == "Lorentz":
            for i in range(0, len(self.curve)):
                if self.curve[i][1] > 0.001:
                    wyniki1 = np.array(Pasmo(self.curve[i][1], self.curve[i][0], self.NrPoints, self.minimum, self.maximum).voigtcurve(0, Q1))
                    wyniki[0,0:] = wyniki1[0,0:]
                    wyniki[1,0:] = wyniki1[1,0:] + wyniki[1,0:]
                    
        elif typeBand == "Voigt":
            for i in range(0, len(self.curve)):
                if self.curve[i][1] > 0.001:
                    wyniki1 = np.array(Pasmo(self.curve[i][1], self.curve[i][0], self.NrPoints, self.minimum, self.maximum).voigtcurve(Q1, Q2))
                    wyniki[0,0:] = wyniki1[0,0:]
                    wyniki[1,0:] = wyniki1[1,0:] + wyniki[1,0:]
                    
        elif typeBand == "Gauss":
            for i in range(0, len(self.curve)):
                if self.curve[i][1] > 0.001:
                    wyniki1 = np.array(Pasmo(self.curve[i][1], self.curve[i][0], self.NrPoints, self.minimum, self.maximum).voigtcurve(Q1, 0))
                    wyniki[0,0:] = wyniki1[0,0:]
                    wyniki[1,0:] = wyniki1[1,0:] + wyniki[1,0:]
                    
        else:
            raise Exception("Wrong curve type: Gauss/Lorentz/Voigt")
                    
        return wyniki

class Results: 
    """Objects are the results to save or draw"""
    def __init__(self, wyniki: np.array, name: str):
        self.wyniki = wyniki 
        self.name = name
    def save(self, label: str):
        """save results 

        Args:
            label (str): Name of envelope eg. Raman or IR
        """
        file_name = "{}_{}.txt"
        results = open(file_name.format(label, self.name), "w")
        results.write("cm-1 Intensity \n")
        results.write("\n")
        colums = self.wyniki.shape 
        for i in range(1, colums[1]): 
            results.write(str(self.wyniki[0, i]) + " " + str(self.wyniki[1, i]) + "\n")
        results.close()
        return
    def print_fig(self, label: str, intensity: list):
        """Print fig 

        Args:
            label (str): Name of envelope eg. Raman or IR
            intensity (list): List of mods 
        """
        x = np.array(self.wyniki[0, 0:])
        y = np.array(self.wyniki[1, 0:])
        Fig_title = "{}_{}"
        plt.xlabel("cm^-1")
        plt.ylabel("Intensity")
        plt.title(Fig_title.format(label, self.name))
        plt.plot(x, y)
        y = int_bonds(x, y, intensity)
        plt.stem(x, y, markerfmt='none', linefmt='red', basefmt='none')
        plt.show()
        return
    def save_fig(self, label: str, intensity: list):
        """save fig 

        Args:
            label (str): Name of envelope eg. Raman or IR
            intensity (list): List of mods 
        """
        x = np.array(self.wyniki[0, 0:]) 
        y = np.array(self.wyniki[1, 0:])
        Fig_title = "{}_{}"
        plt.xlabel("cm^-1")
        plt.ylabel("Intensity")
        plt.title(Fig_title.format(label, self.name))
        plt.plot(x, y)
        y = np.zeros(len(y))
        j = 0
        y = int_bonds(x, y, intensity)
        plt.stem(x, y, markerfmt='none', linefmt='red', basefmt='none') 
        name = "{}_{}.png"
        name1 = name.format(label, self.name)
        plt.savefig(name1, dpi=600)
        plt.close()
        return