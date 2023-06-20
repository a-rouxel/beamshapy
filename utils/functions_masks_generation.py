
import numpy as np

def Simple2DBlazedGratingMask(GridPositionMatrix_X, GridPositionMatrix_Y, period, angles):
    assert len(angles) == 3, "Three angles required for three sections of the mask."

    # Calculate grid sizes
    grid_size_x = GridPositionMatrix_X[-1, -1] - GridPositionMatrix_X[0, 0]
    grid_size_y = GridPositionMatrix_Y[-1, -1] - GridPositionMatrix_Y[0, 0]

    # Initialize the mask
    mask = np.zeros(GridPositionMatrix_X.shape)

    # Create a distance matrix representing the distance from the center
    GridDistanceMatrix = np.sqrt(GridPositionMatrix_X ** 2 + GridPositionMatrix_Y ** 2)
    max_radius = np.sqrt(grid_size_x ** 2 + grid_size_y ** 2) / 2  # maximum radius covering the grid

    # Create angle array to determine the region
    angle_array = np.arctan2(GridPositionMatrix_Y, GridPositionMatrix_X)
    angle_array = (angle_array + np.pi) % (2 * np.pi)  # convert range from [-pi, pi] to [0, 2*pi]

    # Generate the three grating masks
    grating_masks = []
    for angle in angles:
        # Create rotation matrix
        rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])

        # Rotate grid positions
        rotated_positions = np.einsum('ji, mni -> jmn', rotation_matrix,
                                      np.dstack([GridPositionMatrix_X, GridPositionMatrix_Y]))
        rotated_X = rotated_positions[0, :, :]
        grating_masks.append(rotated_X % period)

    # Use circular masks to select regions from the grating masks
    for i in range(3):
        mask[((angle_array >= i * 2 * np.pi / 3) & (angle_array < (i + 1) * 2 * np.pi / 3) & (
                    GridDistanceMatrix <= max_radius))] = grating_masks[i][(
                    (angle_array >= i * 2 * np.pi / 3) & (angle_array < (i + 1) * 2 * np.pi / 3) & (
                        GridDistanceMatrix <= max_radius))]

    return mask

    # Use circular masks to select regions from the grating masks
    for i in range(3):
        if i == 0:
            mask[GridDistanceMatrix <= radii[i]] = grating_masks[i][GridDistanceMatrix <= radii[i]]

        else:
            mask[(GridDistanceMatrix > radii[i-1]) & (GridDistanceMatrix <= radii[i])] = grating_masks[i][(GridDistanceMatrix > radii[i-1]) & (GridDistanceMatrix <= radii[i])]

    return mask



def generate_sampling(grid_size,sampling,focal_length,wavelength):
    delta_x_in = grid_size / sampling
    delta_x_out= wavelength* focal_length / (delta_x_in*sampling)

    x_array_in = np.round(np.linspace(-grid_size / 2, grid_size / 2, sampling), 9)

    x_array_out = np.arange(-sampling / 2, sampling / 2, 1)
    x_array_out *= delta_x_out

    x = np.linspace(-grid_size / 2, grid_size / 2, sampling)
    y = np.linspace(-grid_size / 2, grid_size / 2, sampling)
    GridPositionMatrix_X, GridPositionMatrix_Y = np.meshgrid(x, y)

    return delta_x_in, delta_x_out, x_array_in, x_array_out, GridPositionMatrix_X, GridPositionMatrix_Y

def generate_section_amplitude_masks(GridPositionMatrix_X, GridPositionMatrix_Y):
    # Calculate grid sizes
    grid_size_x = GridPositionMatrix_X[-1, -1] - GridPositionMatrix_X[0, 0]
    grid_size_y = GridPositionMatrix_Y[-1, -1] - GridPositionMatrix_Y[0, 0]

    # Create a distance matrix representing the distance from the center
    GridDistanceMatrix = np.sqrt(GridPositionMatrix_X**2 + GridPositionMatrix_Y**2)
    max_radius = np.sqrt(grid_size_x**2 + grid_size_y**2) / 2  # maximum radius covering the grid

    # Create angle array to determine the region
    angle_array = np.arctan2(GridPositionMatrix_Y, GridPositionMatrix_X)
    angle_array = (angle_array + np.pi) % (2*np.pi)  # convert range from [-pi, pi] to [0, 2*pi]

    masks = []
    for i in range(3):
        mask = np.zeros(GridPositionMatrix_X.shape)
        mask[((angle_array >= i*2*np.pi/3) & (angle_array < (i+1)*2*np.pi/3) & (GridDistanceMatrix <= max_radius))] = 1
        masks.append(mask)

    return masks



def SlitMask(x_array,x0,width):
    mask = np.ones(x_array.shape[0])
    mask[x_array<x0-width/2] = 0
    mask[x_array>=x0+width/2] = 0
    return mask

# function to generate a 1D binary grating mask
def Simple1DGratingMask(x_array,period):

    sampling = x_array.shape[0]
    grid_size = x_array[-1] - x_array[0]
    mask = np.zeros(sampling)
    number_of_periods = int(grid_size / period)

    print("period = ",period)
    print("number_of_periods = ",number_of_periods)
    print("grid_size = ",grid_size)
    print("sampling = ",sampling)

    for per in range(number_of_periods):
        # create a mask numpy array to select x values inside the period range
        min_x_per = per * period - grid_size / 2
        max_x_per = (per + 1) * period - grid_size / 2
        masking_array = (x_array >= min_x_per) & (x_array < max_x_per)

        if per % 2 == 0:
            mask[masking_array] += 1
    return mask


def Simple1DBlazedGratingMask(x_array, period):

    dimension = x_array.shape[0]
    # Generate one period of the ramp function
    ramp_ = np.linspace(-np.pi, np.pi, period+1)
    ramp = ramp_[:-1]

    # calculate how many full periods and extra points we will need



    full_periods = int(dimension // period)
    extra_points = int(dimension % period)

    # create the mask for the full periods
    full_mask = np.tile(ramp, full_periods)
    # add extra points if needed
    if extra_points > 0:
        extra_mask = ramp[:extra_points]
        mask = np.concatenate([full_mask, extra_mask])
    else:
        mask = full_mask

    return mask




def Simple2DWedgeMask(x_array,wavelength,x_position,focal_length):

    angle = np.arctan(x_position/focal_length)

    max_phase = 2*np.pi*angle / np.arctan(wavelength/(x_array.max() - x_array.min()))
    wedge_1D = np.linspace(0, max_phase, x_array.shape[0])
    wedge_2D = np.tile(wedge_1D, ( x_array.shape[0],1))

    return wedge_2D

def sinc_resized(x,step):
    return np.sinc(x/step)

def PhaseReversalMask(GridPositionMatrix_X,GridPositionMatrix_Y,input_waist,sigma_x,sigma_y):


    sinc_step_x = input_waist*sigma_x
    sinc_step_y = input_waist*sigma_y
    depth_param = np.pi

    print("sigma_x = pas reseau / diametre 1/e²: ", np.round(sigma_x,2))
    print("sigma_y = pas reseau / diametre 1/e²: ", np.round(sigma_y,2))
    print("depth_param: ", np.round(depth_param,2)," rad")

    # sinc_mask = np.sinc(GridDistanceMatrix/sinc_step*10*um)
    sinc_mask_x = sinc_resized(GridPositionMatrix_X,sinc_step_x)
    sinc_mask_y = sinc_resized(GridPositionMatrix_Y,sinc_step_y)
    sinc_mask = sinc_mask_x*sinc_mask_y

    M = np.zeros(GridPositionMatrix_X.shape)
    M[sinc_mask < 0] = 1
    M *= depth_param

    return M

def RectangularAmplitudeMask(GridPositionMatrix_X, GridPositionMatrix_Y, angle, width, height):

    mask = np.zeros(GridPositionMatrix_X.shape)
    # rotate the grid
    GridPositionMatrix_X_rot = GridPositionMatrix_X * np.cos(angle) - GridPositionMatrix_Y * np.sin(angle)
    GridPositionMatrix_Y_rot = GridPositionMatrix_Y * np.cos(angle) + GridPositionMatrix_X * np.sin(angle)

    mask[(np.abs(GridPositionMatrix_X_rot) < width/2) & (np.abs(GridPositionMatrix_Y_rot) < height/2)] = 1

    return mask

def SinusAmplitudeArray(GridPositionMatrix_X,GridPositionMatrix_Y,period,angle):

    GridPositionMatrix_X_rot = GridPositionMatrix_X * np.cos(angle) - GridPositionMatrix_Y * np.sin(angle)
    mask = np.sin(2 * np.pi * GridPositionMatrix_X_rot / period)
    return mask


def CosinusAmplitudeArray(GridPositionMatrix_X, GridPositionMatrix_Y, period, angle):
    GridPositionMatrix_X_rot = GridPositionMatrix_X * np.cos(angle) - GridPositionMatrix_Y * np.sin(angle)

    mask = np.cos(2 * np.pi * GridPositionMatrix_X_rot / period)
    return mask

def PiPhaseJumpMask(GridPositionMatrix_X, GridPositionMatrix_Y, orientation, position):

    mask = np.zeros(GridPositionMatrix_X.shape)

    if orientation == "Vertical":
        mask[GridPositionMatrix_Y > position] = np.pi
    elif orientation == "Horizontal":
        mask[GridPositionMatrix_X > position] = np.pi

    return mask



def WeightsMask(input_amplitude,target_amplitude,threshold=10**-1):

    weights =  np.abs(np.divide(target_amplitude,input_amplitude,out=np.ones_like(target_amplitude),where=np.abs(input_amplitude)>threshold))

    weights[weights>1] = 1

    return weights

