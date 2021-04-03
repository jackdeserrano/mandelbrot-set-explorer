import numpy as np
from matplotlib.colors import hsv_to_rgb
from PIL import Image

def normalized_iteration(steps_taken, abs_z):
# https://www.iquilezles.org/www/articles/mset_smooth/mset_smooth.htm
# Map the iteration count of each complex number non-linearly to a value between
# 0 and `steps` using `steps_taken`, the number of steps it takes for the number 
# to exceed `bailout_radius`, and `abs_z`, the magnitude of the complex number that
# exceeds `bailout_radius`. Results in a smooth colour gradient.

    return steps_taken + 3 - np.log2(np.log2(abs_z * abs_z))

def make_mandelbrot_set(real_start, real_end, imag_start, imag_end, height, bailout_radius, steps, mode):
# `bailout_radius` is the threshold the program uses to determine whether a number 
# is diverging or not.
# `steps` is the maximum number of times z \mapsto z ^ 2 + c is composed with itself
# to check if z is greater than the bailout radius; if z exceeds the bailout radius,
# z is not in the set. Increasing `steps` results in increased quality and render
# time.

    real_start = float(real_start)
    real_end = float(real_end)
    imag_start = float(imag_start)
    imag_end = float(imag_end)
    height = int(height)
    bailout_radius = int(bailout_radius)
    steps = int(steps)

    width = \
        int(abs(height * (real_end - real_start) / (imag_end - imag_start)))
    # The width of the image is dependent on the height and the coordinates on the complex
    # plane; it cannot be arbitrary. Such a system keeps the image from being distorted.

    real_axis = \
        np.linspace(real_start, real_end, num = width)
    imag_axis = \
        np.linspace(imag_start, imag_end, num = height)
    complex_plane = \
        np.zeros((height, width), dtype = np.complex_)

    real, imag = np.meshgrid(real_axis, imag_axis)

    complex_plane.real = real
    complex_plane.imag = imag
    # `complex_plane` is a `width`-by-`height` matrix where each element is the corresponding 
    # complex number on the complex plane. 

    pixels = \
        np.zeros((height, width, 3), dtype = np.float_)
    # `pixels` is a `width`-by-`height`-by-three matrix where the three-tuple corresponds to 
    # a colour on the complex plane, eventually determined by the complex number's convergence 
    # or rate of divergence. 

    new_z = np.copy(complex_plane)
    # `new_z` is a matrix like `complex_plane` that will hold the resulting values of complex 
    # numbers after successive iterations of the Mandelbrot mapping. A future masking matrix 
    # checks whether the magnitude of each value exceeds `bailout_radius` and colours the
    # corresponding element in `pixels` accordingly if so.

    new_dz = np.zeros_like(complex_plane)
    # `new_dz` is identical to `new_z` except the fact that it will contain a different mapping
    # found here: http://www.mrob.com/pub/muency/distanceestimator.html.

    is_not_done = np.ones((height, width), dtype = bool)
    # `is_not_done` is a `width`-by-`height` Boolean matrix that indicates whether a 
    # complex number has exceeded `bailout_radius`. Such a matrix is necessary to avoid 
    # any unnecessary computation.
    
    if mode == 'classic':
    # If the user wants the "classic Mandelbrot colouring."

        for i in range(steps):
        # The maximum number of iterations is `steps`.

            new_z[is_not_done] = \
                new_z[is_not_done] ** 2 + complex_plane[is_not_done]
            # Each element in `new` that has not yet exceeded `bailout_radius` is mapped
            # to a new value by the Mandelbrot mapping.
            
            mask = np.logical_and(np.absolute(new_z) > bailout_radius, is_not_done)
            # An element in `mask` is `True` iff its magnitude exceeds `bailout_radius` and
            # its magnitude has not previously exceeded `bailout_radius`.

            pixels[mask, :] = (i, 1 - i/steps, 1 - i/steps) 
            # If a given complex number meets the above conditions, it is coloured, for now,
            # based on the number of iterations it took to exceed `bailout_radius`.

            is_not_done = np.logical_and(is_not_done, np.logical_not(mask))
            # `is_not_done` is updated based on the points that were coloured in this iteration. 

        new_after_mask = np.zeros_like(complex_plane)
        new_after_mask[np.logical_not(is_not_done)] = new_z[np.logical_not(is_not_done)]
        new_after_mask[is_not_done] = np.e ** 2 
        # `new_after_mask` consists of complex numbers on the plane corresponding to the number
        # whose magnitude exceeded the bailout radius. `new_after_mask[is_not_done] = np.e ** 2`
        # because this is the value necessary to achieve an output of `steps` from  
        # `normalized_iteration`. Arbitrary values for `new_after_mask[is_not_done]`also colour 
        # the pixel black, but this method has an comprehendible reason.

        pixels[:, :, 0] = \
            normalized_iteration(pixels[:, :, 0], np.absolute(new_after_mask)) / steps
        # Smooth out the colour gradient of the image by putting it through `normalized_iteration`.
        # Normalizes the values by dividing by `steps`.

    elif mode == 'grayscale':
    # If the user wants a colouring where the colouring is grayscaled and black represents a 
    # number in the set.

        for i in range(steps):

            new_z[is_not_done] = \
                new_z[is_not_done] ** 2 + complex_plane[is_not_done]

            mask = np.logical_and(np.absolute(new_z) > bailout_radius, is_not_done)

            pixels[mask, :] = (0, 0, 1 - i/steps)

            is_not_done = np.logical_and(is_not_done, np.logical_not(mask))

    elif mode == 'inverse_grayscale':
    # If the user wants a colouring where the colouring is grayscaled and white represents a 
    # number in the set.

        pixels[:] = (0, 0, 1)

        for i in range(steps):

            new_z[is_not_done] = \
                new_z[is_not_done] ** 2 + complex_plane[is_not_done]

            mask = np.logical_and(np.absolute(new_z) > bailout_radius, is_not_done)

            pixels[mask, :] = (0, 0, i/steps)

            is_not_done = np.logical_and(is_not_done, np.logical_not(mask))

    elif mode == 'distance_estimator':
    # If the user wants the distance estimator colouring (default, rainbow).

        for i in range(steps):

            new_dz[is_not_done] = \
                2 * new_z[is_not_done] * new_dz[is_not_done] + 1
            # d / dz z ^ 2 + c

            new_z[is_not_done] = \
                new_z[is_not_done] ** 2 + complex_plane[is_not_done]
            
            mask = np.logical_and(np.absolute(new_z) > bailout_radius, is_not_done)

            z = np.abs(new_z[mask])
            dz = np.abs(new_dz[mask])
            # If a complex number has exceeded `bailout_radius`, we need the magnitude of `z` and 
            # `dz` generated by that number to compute the distance.  

            pixels[mask, 0] = 2 * np.log(z) * z / dz
            # Refer to http://www.mrob.com/pub/muency/distanceestimator.html.

            pixels[mask, 1:] = (0.5, 1 - i/steps)

            is_not_done = np.logical_and(is_not_done, np.logical_not(mask))

        pixels[is_not_done, :] = (0, 0, 0)
        pixels[:, :, 0] /= np.amax(pixels[:, :, 0])

    return [(hsv_to_rgb(np.flipud(pixels)) * 255).astype(np.uint8), width]
    # Convert the image to RGB, flip it upside down (the set would be upside down otherwise),
    # and bring the values between 0 and 255. Return this image as well as the image width.

# Credit to:
# http://www.mrob.com/pub/muency/distanceestimator.html
# https://en.wikibooks.org/wiki/Fractals/Iterations_in_the_complex_plane/Julia_set#DEM.2FJ
# https://en.wikipedia.org/wiki/Plotting_algorithms_for_the_Mandelbrot_set
# https://www.iquilezles.org/www/articles/mset_smooth/mset_smooth.htm
# and the multifarious unidentifiable websites I used to familiarize myself with fractal
# generation and colouring. I feel incredibly well-versed in fractal colouring methods
# and the mathematics behind those methods, but an overall lack of documentation on
# how to get a satisfying colouring from the generated values led to countless hours of
# unsuccessful trial and error and an overall subpar program in the colouring category.  
