import numpy as np
from scipy.optimize import brentq

def wrap_phase(phase):
    """
    Wraps the phase between -pi and pi.

    Args:
        phase (np.ndarray): 2D array with the phase (in rad).

    Returns:
        np.ndarray: 2D array with the wrapped phase (in rad).

    """

    return np.angle(np.exp(1j * phase))

def correct(phase, correction_a_values, correction_tab):
    """
    Corrects the mask phase using the correction table.

    Args:
        phase (np.ndarray): 2D array with the phase (in rad).
        correction_a_values (np.ndarray): 1D array with the correction a values (between 0 and 1).
        correction_tab (np.ndarray): 2D array with the correction table.

    """
    return correct_modulation_values(phase, correction_a_values, correction_tab)



def WeightsMask(input_amplitude,target_amplitude,threshold=10**-1):

    weights =  np.abs(np.divide(target_amplitude,input_amplitude,out=np.ones_like(target_amplitude),where=np.abs(input_amplitude)>threshold))

    weights[weights>1] = 1

    return weights


def theorical_deformation_sinc(x):
    """
    Computes the theorical deformation of the sinc function.

    Args:
        x (np.ndarray): 1D array with the x values.

    Returns:
        np.ndarray: 1D array with the theorical deformation of the sinc function.

    """

    a = np.sin(np.pi * (1 - x))
    b = (np.pi * (1 - x))
    theorical_amplitude_modulation = np.divide(a, b, out=np.ones_like(a), where=b != 0)

    return theorical_amplitude_modulation

def root_theorical_deformation_sinc(x,c):
    """
    Computes the root of the theorical deformation of the sinc function.

    Args:
        x (np.ndarray): 1D array with the x values.
        c (float): Value of the theorical deformation of the sinc function.

    """

    return theorical_deformation_sinc(x) - c

def generate_correction_tab(step,func):
    """
    Generates the correction table.

    Args:
        step (int): Number of points of the correction table.
        func (function): Function to correct.

    Returns:
        np.ndarray: 1D array with the correction a values (between 0 and 1).

    """

    a_values = np.linspace(0.001,0.999,step-2)
    correction_tab = np.zeros_like(a_values)

    for i,a in enumerate(a_values):
        correction_tab[i] = brentq(func, 0, 1, args=(a,))

    a_values = list(a_values)
    a_values.insert(0,0)
    a_values.append(1)
    correction_tab = list(correction_tab)
    correction_tab.insert(0,0)
    correction_tab.append(1)

    return a_values,correction_tab

def correct_modulation_values(modulation_values,a_values,correction_tab):
    """
    Interpolates the correction table

    Args:
        modulation_values (np.ndarray): 2D array with the modulation values.
        a_values (np.ndarray): 1D array with the correction a values (between 0 and 1).
        correction_tab (np.ndarray): 2D array with the correction table.

    Returns:
        np.ndarray: 2D array with the corrected modulation values.

    """

    return np.interp(modulation_values,a_values,correction_tab)







