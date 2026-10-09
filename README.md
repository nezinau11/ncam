# ncam

A camera app written in Python for the MaixCAM2 platform with a focus on dithering.

# Features

- Optimized using numba for real-time dithered display
- Multiple dithering algorithms
    - Quantization with custom palettes
        - Uses CIEDE2000 color difference algorithm for human perception accurate results
        - Fast color quantization using pre-computed look-up tables
    - Error diffusion algorithms
        - Atkinson
        - Floyd-Steinberg
        - Stucki
    - Ordered dithering
        - Many different patterns
    - Artsy experimental dithering algorithms
- Automatic/manual exposure, ISO controls
- Focus peaking display for focus adjustment

# Notes

Since the dithering methods are compiled with numba upon first run it takes a while to switch dithering methods until they are compiled and cached.

# Custom palettes

To add custom palettes the `colorcube.py` utility must be used. It requires the `Numpy`, `PIL` and `skimage` Python modules, run it on a PC for quick calculations. To use it create a folder named `palettes` and place the custom palettes in Paint.NET `.txt` format there. Run the `colorcube.py` utility and it will create `.npy` pre-computed LUTs, which must be placed in the applications `palettes` folder.

# Acknowledgments

The app bundles the [pixeif](https://pypi.org/project/piexif/) library and the [NotCourierSans](https://www.fontsquirrel.com/fonts/notcouriersans) font. Some of the ordered dithering matrices have been taken from the excellent dithering tool [Ditherista](https://github.com/robertkist/ditherista).
