# Mandelbrot Set Explorer
## Introduction
This project was done in fulfillment of Mr. Richard Van De Wiele's ICS4U culminating assignment. The project-delineating presentation is [here](presentation/presentation.tex). The project's flowchart is [here](flowchart.pdf). 

This project displays the Mandelbrot set and allows the user to zoom in on desired sections, change colour schemes, save zooms, and open previously-saved zooms. Though the result appears subpar, I am delighted with the project's outcome and satisfied with the amount of time I devoted to it. Thank you to [Josh](https://github.com/Taggagii) for helping me debug the program and teaching me the Tkinter essentials. 

## Setup
To download this project, go into the terminal or command line and run 
```
git clone https://github.com/jackdeserrano/mandelbrot-set-explorer
```
This project requires specific packages. To ensure you have the correct versions, run either
```
pip install -r requirements.txt
```
or 
```
pip3 install -r requirements.txt
```
If you cannot yet use the `pip` or `pip3` commands, run 
```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
```
followed by
```
python get-pip.py
```
Then try accessing `requirements.txt` again.

Since you have installed the necessary packages, you are ready to begin. In the same directory as the project, run
```
python main.py
```

## Commands
### Zooming in
Click and drag to select a part of the set into which to zoom. The program gets the pixel coordinates of the vertices of the box you selected, maps them to the appropriate complex numbers, and generates the zoomed-in set based on those numbers.
### Changing render quality
Press the up or down arrows to increase or decrease the quality and render time of the zoom. When the program detects one of these keypresses, `self.steps`, the maximum number of iterations the program will run to check if a complex number has exceeded `self.bailout_radius`, is increased or decreased by a factor of two.
### Changing colour scheme
Press either the `c`, `d`, `g`, or `i` keys to change the current colour scheme. Try each of them out for yourself.

`c` stands for classic colouring. It uses the [normalized iteration count algorithm](https://www.iquilezles.org/www/articles/mset_smooth/mset_smooth.htm) to smooth out the resulting colour gradient. In essence, this setting colours a complex number based on how many iterations it took for the result to exceed `self.bailout_radius`. It utilizes the previously-mentioned algorithm to reduce [banding](https://en.wikipedia.org/wiki/Plotting_algorithms_for_the_Mandelbrot_set#Histogram_coloring).

`d` stands for either distance estimator or default, whichever you prefer. It uses this [distance estimating algorithm](http://www.mrob.com/pub/muency/distanceestimator.html) to assign each complex number an approximate distance to the closest point in the set. The program maps these distances between zero and one (for [HSV colouring](https://en.wikipedia.org/wiki/HSL_and_HSV)), where small distances are coloured red, and large distances are coloured violet.

`g` stands for grayscale and `i` stands for inverse grayscale. These settings grayscale the classic colouring.

### Saving zooms
Press `s` to save a zoom. You will be prompted to submit what you would like to name the file. From there, the image is saved in the `images` folder and the image's information is saved in `images.txt` for future reference.

### Opening zooms
Press `o` to open a zoom. You will be prompted to enter the name of the image you previously saved. If the name exists, the program will open the image and allow you to interact with it.
