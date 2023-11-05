from beamshapy.mask_generation.functions_masks_generation import *
from beamshapy.spatial_profiles.functions_basic_shapes import *

def fresnel_lens(GridPositionMatrix_X_out, GridPositionMatrix_Y_out, radius,parabola_coef,hyper_gauss_order):

    parabola = ParabolaMask(GridPositionMatrix_X_out, GridPositionMatrix_Y_out, parabola_coef)
    wrap_parabola = parabola % 1

    x_array_out = GridPositionMatrix_X_out[0,:]
    fresnel_lens = wrap_parabola * supergaussian2D(x_array_out, hyper_gauss_order, radius)

    return fresnel_lens
