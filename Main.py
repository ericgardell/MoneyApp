import time
import timeit
import tkinter as tk    # Module that the GUI itself uses
import matplotlib
import matplotlib.animation as animation
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt

register_matplotlib_converters()
matplotlib.use("TkAgg")       # allow matplotlib to work better with TKinter
style.use("ggplot")
LARGE_FONT = ("Verdana", 12)  # font's family is Verdana, font's size is 12
HEIGHT = 500    # Plot canvas Height in pixels
WIDTH = 500     # Plot canvas Width in pixels
YELLOW = "#476042"  # Assigning color code to variable for easier use
CENTER = tk.CENTER

# Initialize the figure on the plotting page
f = Figure(figsize=(5, 4), dpi=100)
a = f.add_subplot(111)
minutes = mdates.MinuteLocator()    # Helps reduce number of ticks on x-axis


def animate(i):  # This function is called at the bottom of the script with the assignment of ani
    if app.frames[PlotPage].var.get():      # This if statement checks whether the checkbox is checked or not
        try:    # Error handling, allows program to keep running in the case of a FileNotFoundError
            x_axis = f.axes[0]
            x_axis.xaxis.set_major_locator(minutes)
            a.clear()   # Clear the plot after everytime so it is on the relevant data
            a.plot(app.frames[HomePage].years, app.frames[HomePage].balance)
            a.set_xlabel('Years')
            a.set_ylabel('Balance')
        except ValueError:   # no file was found
            # tell user no file was found, then reset back to normal
            print('data not calculated')
            app.frames[PlotPage].plot_checkbox.deselect()
            app.frames[PlotPage].plot_checkbox['text'] = 'data not calculated'
            app.frames[PlotPage].update()
            time.sleep(1.5)
            app.frames[PlotPage].plot_checkbox['text'] = 'Check Box to Enable Live Plotting'
            app.frames[PlotPage].update()


class Intry(tk.Entry):
    def __init__(self, master=None, **kwargs):
        self.var = tk.StringVar()
        tk.Entry.__init__(self, master, textvariable=self.var, **kwargs)
        self.old_value = ''
        self.var.trace('w', self.check)
        self.get, self.set = self.var.get, self.var.set

    def check(self, *args):
        if self.get().isdigit():
            # the current value is only digits; allow this
            self.old_value = self.get()
        else:
            # there's non-digit characters in the input; reject this
            self.set(self.old_value)


class MainWindow(tk.Tk):
    # This is the MainWindow of the GUI
    # All pages of the app are drawn on top of/ inside of this window
    # When a MainWindow is created the __init__ function is ran
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("500x500")    # Set the window to 500x500 pixels
        self.resizable(False, False)    # Turn off resizing in both directions
        # Call the create_file function when a MainWindow is created
        self.data_in_file = False       # Initially the file is empty

        # A template to create the pages of the GUI
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}

        # Create the pages as requested, new pages are their own classes
        for F in (HomePage, PlotPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    # method to display the requested GUI page
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class HomePage(tk.Frame):
    # This class is the HomePage, it is called in the for-loop in the MainWindow __init__ function
    def __init__(self, parent, controller):
        self.controller = controller
        self.running = False    # running is false until run button clicked AND encoder is detected
        tk.Frame.__init__(self, parent)

        # Text to display on the top of the pages
        label = tk.Label(self, text="Compound Interest Calculator", font=LARGE_FONT)
        label.place(relx=.5, y=15, anchor=CENTER)

        self.label1 = tk.Label(self, text='Initial Account Value', font=("Helvetica", 14), padx=20)
        self.label1.place(x=112.5, y=175, anchor='w', relwidth=.45)
        self.entry1 = Intry(self, justify=CENTER)
        self.entry1.place(x=387.5, y=175, relwidth=.1, anchor='e')
        self.entry1.set(1500)

        self.label2 = tk.Label(self, text='Account Contributions', font=("Helvetica", 14), padx=25)
        self.label2.place(x=112.5, y=200, anchor='w', relwidth=.45)
        self.entry2 = Intry(self, justify=CENTER)
        self.entry2.place(x=387.5, y=200, relwidth=.1, anchor='e')
        self.entry2.set(500)

        self.label3 = tk.Label(self, text='Contributions per year', font=("Helvetica", 14), padx=30)
        self.label3.place(x=112.5, y=225, anchor='w', relwidth=.45)
        self.entry3 = Intry(self, justify=CENTER)
        self.entry3.place(x=387.5, y=225, relwidth=.1, anchor='e')
        self.entry3.set(12)

        self.label4 = tk.Label(self, text='Annualized Returns', font=("Helvetica", 14), padx=35)
        self.label4.place(x=112.5, y=250, anchor='w', relwidth=.45)
        self.entry4 = Intry(self, justify=CENTER)
        self.entry4.place(x=387.5, y=250, relwidth=.1, anchor='e')
        self.entry4.set(8)

        self.label5 = tk.Label(self, text='Years to Grow', font=("Helvetica", 14), padx=40)
        self.label5.place(x=112.5, y=275, anchor='w', relwidth=.45)
        self.entry5 = Intry(self, justify=CENTER)
        self.entry5.place(x=387.5, y=275, relwidth=.1, anchor='e')
        self.entry5.set(10)

        # button to go to plot page
        self.button1 = tk.Button(self, text="Calculate", bg='white',
                                 command=lambda: calculate())
        self.button1.place(x=250, y=315, relwidth=.55, anchor=CENTER)

        self.label6 = tk.Label(self, text='Final Value', font=("Helvetica", 14), padx=4)
        self.label6.place(x=250, y=350, anchor=CENTER)

        # button to go to plot page
        self.button1 = tk.Button(self, text="Show Plot",
                                 command=lambda: controller.show_frame(PlotPage))
        self.button1.place(relx=.025, rely=.15, relwidth=.15, anchor='w')

        self.balance = []
        self.total_contributions = []
        self.years = np.arange(1, int(self.entry5.get()))

        # nums = []
        # while (num := input("Enter a number: ")).isdigit():
        #    nums.append(num)

        def calculate():
            self.balance = [int(self.entry1.get())]
            self.total_contributions = [self.balance[0]]
            self.years = np.arange(1, int(self.entry5.get()))
            contributions = int(self.entry2.get())
            c_per_year = int(self.entry3.get())
            annual = int(contributions * c_per_year)
            rate = 1 + (int(self.entry4.get()) / 100)

            for i in self.years:
                self.balance.append((self.balance[i-1] + annual) * rate)
                self.total_contributions.append(self.total_contributions[i-1] + annual)
            line_one = 'Final Account Value: $' + f'{round(self.balance[-1], 2):,}'
            line_two = f'Total Contributions: ${round(self.total_contributions[-1], 2):,}'
            self.label6['text'] = line_one + '\n' + line_two
            self.years = np.insert(self.years, 0, 0)
            print(self.balance, '\n', self.years)


class PlotPage(tk.Frame):
    # This class creates the plot page of the GUI
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Label at the top of the page
        label = tk.Label(self, text="Slack Adjuster Sensing Road Test", font=LARGE_FONT)
        label.place(relx=.5, y=15, anchor=CENTER)

        # The label above the status 'LED'
        self.reading_label = tk.Label(self, text='here')
        self.reading_label.place(x=250, y=40, anchor=CENTER)

        # canvas area for the graph itself
        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().place(relx=.5, rely=.5, relheight=.5, relwidth=.45, anchor=CENTER)

        # adding the matplotlib toolbar at the bottom of the page
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.place(relx=.5, rely=.55, relheight=.75, relwidth=.98, anchor=CENTER)

        # Button to navigate back to the home page
        button1 = tk.Button(self, text="Home", command=lambda: controller.show_frame(HomePage))
        button1.place(relx=.025, rely=.145, relwidth=.15, anchor='w')

        # Checkbox to toggle live plotting
        self.var = tk.BooleanVar()
        self.plot_checkbox = tk.Checkbutton(self, text='Check Box to Enable Live Plotting',
                                            variable=self.var)
        self.plot_checkbox.place(relx=.975, rely=.145, anchor='e')


if __name__ == '__main__':
    app = MainWindow()
    ani = animation.FuncAnimation(f, animate, interval=1000)
    app.mainloop()
