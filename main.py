from tkinter import *
from PIL import Image, ImageTk
from mandelbrot import *

class Mandelbrot(Frame):
    def __init__(self, master):
    # Run on the call of `Mandelbrot`.

        Frame.__init__(self, master = None)
        self.master.title('Mandelbrot Set Explorer')
        self.height = 700
        self.x = 0
        self.y = 0
        self.image = None

        self.real_start = -2
        self.real_end = 1
        self.imag_start = -1
        self.imag_end = 1
        # Initialize the bounds for the image on the complex plane.

        self.bailout_radius = 2 **10
        self.steps = 2 ** 8

        self.mandelbrot = make_mandelbrot_set(self.real_start, self.real_end, self.imag_end, self.imag_start, self.height, self.bailout_radius, self.steps, 'distance_estimator')
        # Generate the image.

        self.width = self.mandelbrot[1]

        self.canvas = Canvas(self, cursor = 'cross', width = self.width, height = self.height)
        # Initialize the canvas to hold the image.

        self.config_set(self.mandelbrot[0])
        # Set up the image to be displayed on the canvas.

        self.canvas.grid(row = 0, column = 0, sticky = N + S + E + W)
        # Display the image on the canvas.

        self.canvas.bind('<ButtonPress-1>', self.button_press)
        self.canvas.bind('<B1-Motion>', self.move)
        self.canvas.bind('<ButtonRelease-1>', self.button_release)
        self.canvas.bind_all('<Key>', self.key_press)
        # Allow for the detection of key and button presses.

        self.mode = 'distance_estimator'
        self.rectangle = None
        self.start_x = None
        self.start_y = None
        self.new_real_start = None
        self.new_imag_start = None
        self.new_real_end = None
        self.new_imag_end = None
        self.cursor_x = None
        self.cursor_y = None
        self.previous_list = []
        self.next_list = []
        self.task_running = False
        self.moving = False
        self.saved_images = []

    def map_pixel(self, x, y):
    # Map a pixel to its corresponding complex number based on the width and height of the image 
    # and the complex bounds on the plane.

        real_part = \
            self.real_start + (x / self.width) * (self.real_end - self.real_start)
        imag_part = \
            self.imag_start + (y / self.height) * (self.imag_end - self.imag_start)
        return real_part, imag_part
    
    def generate_new_set(self, coordinates):
    # Display the zoomed set based on the box drawn.
        x_1, y_1, x_2, y_2 = coordinates

        dx = abs(x_2 - x_1)
        dy = abs(y_2 - y_1)
        
        if dx < 2 or dy < 2:
        # Do not zoom in if the box drawn was negligibly small.
            self.canvas.delete(self.rectangle)
            self.rectangle = None
            return 0
        
        ratio = dx / dy 

        if ratio > 3 / 2:
            stabilizer = ((2 / 3) * dx - dy) / 2
            y_1 -= stabilizer
            y_2 += stabilizer

        elif ratio < 3 / 2:
            stabilizer = ((3 / 2) * dy - dx) / 2
            x_1 -= stabilizer
            x_2 += stabilizer
        # If the box drawn is not three-by-two, adjust the image such that it is displayed 
        # as a three-by-two image.
            
        self.new_real_start, self.new_imag_start = self.map_pixel(x_1, y_1)
        self.new_real_end, self.new_imag_end = self.map_pixel(x_2, y_2)
        # Get the new bounds for the zoomed set based on the box drawn. Different variables are
        # used (`self.new_real_start` instead of `self.real_start` etc.) because the `self.map_pixel`
        # call relies on the value of `self.real_start` etc. to properly map the pixel.

        try:
            self.mandelbrot = \
                make_mandelbrot_set(self.new_real_start, self.new_real_end, self.new_imag_end, self.new_imag_start, self.height, self.bailout_radius, self.steps, self.mode)

        except ZeroDivisionError:
            self.canvas.delete(self.rectangle)
            self.rectangle = None
            return 0
        # If the `make_mandelbrot_set` call results in zero division (specifically when `width` is initialized)
        # then do not generate a new set, otherwise generate the new set.

        self.real_start, self.imag_start = self.new_real_start, self.new_imag_start
        self.real_end, self.imag_end = self.new_real_end, self.new_imag_end

        self.width = self.mandelbrot[1]

        self.config_set(self.mandelbrot[0])
        # Display the newly-generated set.

    def config_set(self, pixels):
    # From a three-dimensional array of RGB values display the image to the window.

        self.image = Image.fromarray(pixels)
        # Create a PIL image from the array.

        width = height = self.width
        self.image.thumbnail((width, height))
        # Make the image fit the window.

        width, height = self.image.size
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor = 'nw', image = self.photo_image)
        # Display the image on the canvas.

    def button_press(self, event):
    # Get the coordinates of the initial click for the box.

        if not self.task_running:
            self.task_running = True
            self.start_x = self.canvas.canvasx(event.x)
            self.start_y = self.canvas.canvasy(event.y)

            if not self.rectangle:
                self.rectangle = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline = 'red')
            # Create the rectangle.

            self.task_running = False

    def move(self, event):
    # Expand the box as the mouse drags.

        if not self.task_running or self.moving:
            self.task_running = True
            self.moving = True
            self.cursor_x = self.canvas.canvasx(event.x)
            self.cursor_y = self.canvas.canvasy(event.y)
            
            self.canvas.coords(self.rectangle, self.start_x, self.start_y, self.cursor_x, self.cursor_y)

    def button_release(self, event):
    # Generate the zoomed set based on the drawn box once the mouse is released.

        if self.moving:

            self.moving = False
            self.task_running = True

            self.previous_list.append(
                [self.mandelbrot[0], self.real_start, self.real_end, self.imag_end, self.imag_start, self.steps, self.bailout_radius, self.mode]
                )
            # Append the current set's information to a list in case the user wants to go back.

            self.generate_new_set(self.canvas.coords(self.rectangle))
            # Generate the new set

            self.next_list = []
            # There should not be anything on which to zoom back in once a new zoom is complete.

            self.canvas.delete(self.rectangle)
            self.rectangle = None
            # Delete the box.

            self.task_running = False

    def key_press(self, event):
    # Detect a key press.

        if not self.task_running:

            self.task_running = True

            if event.keysym == 'Left':
            # If the user wants to go to the previous image.

                if self.previous_list != []:
                # If the current image is not the original.

                    self.next_list.append(
                        [self.mandelbrot[0], self.real_start, self.real_end, self.imag_end, self.imag_start, self.steps, self.bailout_radius, self.mode]
                        )
                    # Append the current image to `next_list` so that the user can go zoom back in to it.

                    self.real_start, self.real_end, self.imag_end, self.imag_start = \
                        self.previous_list[-1][1:5]
                    self.steps = self.previous_list[-1][5]
                    self.bailout_radius = self.previous_list[-1][6]
                    self.mode = self.previous_list[-1][7]
                    self.config_set(self.previous_list[-1][0])
                    # Display the previous image.

                    del self.previous_list[-1]
                    self.mandelbrot[0] = np.array(self.image)
            
            elif event.keysym == 'Right':
            # If the user wants to go to the previously-zoomed-into image.

                if self.next_list != []:
                # If the user has gone to a previously-viewed image.

                    self.previous_list.append(
                        [self.mandelbrot[0], self.real_start, self.real_end, self.imag_end, self.imag_start, self.steps, self.bailout_radius, self.mode]
                        )
                    # Append the current image to `previous_list` so that the user can go back to it.

                    self.real_start, self.real_end, self.imag_end, self.imag_start = \
                        self.next_list[-1][1:5]
                    self.steps = self.next_list[-1][5]
                    self.bailout_radius = self.next_list[-1][6]
                    self.mode = self.next_list[-1][7]
                    self.config_set(self.next_list[-1][0])
                    # Zoom back in to the image.

                    del self.next_list[-1]
                    self.mandelbrot[0] = np.array(self.image)

            elif event.keysym == 'Up': 
            # If the user wants to double the quality of the image (double `steps`), do just that and 
            # update the image. Render time is longer.

                self.steps <<= 1
                self.mandelbrot = \
                    make_mandelbrot_set(self.real_start, self.real_end, self.imag_end, self.imag_start, self.height, self.bailout_radius, self.steps, self.mode)
                self.config_set(self.mandelbrot[0])

            elif event.keysym == 'Down': 
            # If the user wants to halve the quality of the image (halve `steps`), do just that and update 
            # the image. Render time is shorter.

                self.steps >>= 1
                self.mandelbrot = \
                    make_mandelbrot_set(self.real_start, self.real_end, self.imag_end, self.imag_start, self.height, self.bailout_radius, self.steps, self.mode)
                self.config_set(self.mandelbrot[0])

            elif event.keysym == 'c':
                self.change_mode('classic')

            elif event.keysym == 'g':
                self.change_mode('grayscale')

            elif event.keysym == 'i':
                self.change_mode('inverse_grayscale')

            elif event.keysym == 'd':
                self.change_mode('distance_estimator')

            elif event.keysym == 's':
            # If the user wants to save the image, let the user choose the name and add the image's 
            # relevant information to `images.txt`.

                self.images_txt = open('images.txt', 'a+')
                self.images_txt.seek(0)

                self.save_window = Tk()
                self.save_window.protocol('WM_DELETE_WINDOW', self.user_closed_window)
                self.save_window.title('Save Zoom')
                self.save_window.resizable(False, False)
                self.name = Label(self.save_window, text = 'Name')
                self.name.grid(row = 0, column = 0, sticky = NW)

                self.save_entry = Entry(self.save_window, width = 30)
                self.save_entry.grid(row = 0, column = 1, sticky = NE)

                self.save_button = Button(self.save_window, text = 'Save', command = self.save_image)
                self.save_button.grid(row = 1, column = 0, columnspan = 2, sticky = SW)
                self.save_window.mainloop()
                    
            elif event.keysym == 'o':
            # If the user wants to open a previously-saved image, prompt them to type in the
            # name of the image. Look for the name in `images.txt`; if it is there, render
            # the image.

                self.open_window = Tk()
                self.open_window.protocol('WM_DELETE_WINDOW', self.user_closed_window)
                self.open_window.title('Open Zoom')
                self.open_window.resizable(False, False)
                self.prompt = Label(self.open_window, text = 'Enter image name (omit .png)')
                self.prompt.grid(row = 0, column = 0, sticky = NW)

                self.entry = Entry(self.open_window, width = 30)
                self.entry.grid(row = 0, column = 1, sticky = NE)

                self.button = Button(self.open_window, text = 'Open', command = self.open_set)
                self.button.grid(row = 1, column = 0, columnspan = 2, sticky = SW)
                self.open_window.mainloop()

            self.task_running = False


    def change_mode(self, mode):
    # If the user wants to change the colouring, call this function.

        if self.mode != mode:

            self.previous_list.append(
                [self.mandelbrot[0], self.real_start, self.real_end, self.imag_end, self.imag_start, self.steps, self.bailout_radius, self.mode]
                )
            self.mode = mode
            self.mandelbrot = \
                make_mandelbrot_set(self.real_start, self.real_end, self.imag_end, self.imag_start, self.height, self.bailout_radius, self.steps, self.mode)
            self.config_set(self.mandelbrot[0])
            self.mandelbrot[0] = np.array(self.image)

    def user_closed_window(self):
    # Make sure the program properly handles the user manually closing the window.

        self.open_window.destroy()
        self.task_running = False

    def save_image(self):
    # If the user wants to save the current image, call this function. Prompt the user to
    # choose a name for the file and write appropriate information to `images.txt`. 

        name = self.save_entry.get().replace(' ', '_')
        self.images_txt.write(f'{name} {self.real_start} {self.real_end} {self.imag_end} {self.imag_start} {self.height} {self.bailout_radius} {self.steps} {self.mode}\n') 
        self.image.save(f'images/{name}.png')
        self.images_txt.close()
        self.save_window.destroy()
        self.task_running = False


    def open_set(self):
    # If the user wants to open a previously-saved image, call this function. Prompt the user
    # to enter the name of the image they want to open, and see if it exists. If it does not,
    # tell the user to try again. If it does, get the relevant information from `images.txt`
    # and display the image.

        self.images_txt = open('images.txt', 'a+')
        self.images_txt.seek(0)
        self.set_name = self.entry.get().replace(' ', '_')
        
        if not self.set_name in [i[0] for i in self.saved_images]:
            self.saved_images = [i.split() for i in self.images_txt.readlines()]

        if not self.set_name in [i[0] for i in self.saved_images]:
            self.error_message = Label(self.open_window, text = 'Not found. Try again or exit.')
            self.error_message.grid(row = 1, column = 1, columnspan = 1, sticky = SW)
            self.error_message.configure(fg = 'red')

        else:

            for i, j in enumerate(self.saved_images):
                if self.set_name == j[0]:
                    index = i
                    break

            self.previous_list.append(
                [self.mandelbrot[0], self.real_start, self.real_end, self.imag_end, self.imag_start, self.steps, self.bailout_radius, self.mode]
                )

            self.mandelbrot = \
                    make_mandelbrot_set(*self.saved_images[index][1:])

            self.real_start, self.real_end, self.imag_end, self.imag_start = \
                        [float(i) for i in self.saved_images[index][1:5]]

            self.steps = int(self.saved_images[index][7])
            self.bailout_radius = int(self.saved_images[index][6])
            self.mode = self.saved_images[index][8]

            self.images_txt.close()
            self.config_set(self.mandelbrot[0])
            self.mandelbrot[0] = np.array(self.image)

            self.open_window.destroy()
            self.task_running = False


if __name__ == '__main__':
    root = Tk()
    root.resizable(False, False)
    app = Mandelbrot(root)
    app.pack()
    root.mainloop()