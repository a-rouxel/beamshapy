from beamshapy.spatial_profiles.functions_basic_shapes import ParabolaMask, supergaussian2D

def fresnel_lens(GridPositionMatrix_X_out, GridPositionMatrix_Y_out, radius, parabola_coef,hyper_gauss_order):
    """
    Function to generate a Fresnel lens intensity profile

    Args:
        GridPositionMatrix_X_out (np.ndarray): X coordinates of the target grid
        GridPositionMatrix_Y_out (np.ndarray): Y coordinates of the target grid
        radius (float): Radius of the Fresnel lens (in m)
        parabola_coef (float): Coefficient of the parabola profile (no units)
        hyper_gauss_order (int): Order of the hyper-gaussian profile

    Returns:
        np.ndarray: Fresnel lens intensity profile
    """

    parabola = ParabolaMask(GridPositionMatrix_X_out, GridPositionMatrix_Y_out, parabola_coef)
    wrap_parabola = parabola % 1

    x_array_out = GridPositionMatrix_X_out[0,:]

    return wrap_parabola * supergaussian2D(x_array_out, hyper_gauss_order, radius)
