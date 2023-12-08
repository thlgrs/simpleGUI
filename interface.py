import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class Problem:
    def __init__(self, name: str, parameters: dict):
        """
        Represents a scientific problem.

        Parameters:
        - name (str): The name of the problem.
        - parameters (dict): The parameters required for the problem.
        """
        self.name = name
        self.parameters = parameters

    def calculate_result(self):
        """
        Calculate and return the result of the problem.
        """
        raise NotImplementedError("Subclasses must implement the calculate_result method")

    def plot_result(self):
        """
        Optional: Plot the result of the problem.
        """
        pass

    def text_result(self):
        """
        Return the result of the problem as a string.
        """
        raise NotImplementedError("Subclasses must implement the text_result method")

    def __str__(self):
        """
        String representation of the problem.
        """
        param_str = ', '.join(f"{key}={value}" for key, value in self.parameters.items())
        return f"{self.name} with parameters: {param_str}"

class RectangularVolumeProblem(Problem):
    def __init__(self):
        super().__init__("Rectangular Volume", {'length': 1.0, 'width': 1.0, 'height': 1.0})
        self.result = None

    def calculate_result(self):
        """
        Calculate and return the volume of a rectangular prism.
        """
        self.result = self.parameters['length'] * self.parameters['width'] * self.parameters['height']

    def plot_result(self):
        """
        Plot the result of the problem.
        """
        plt.bar(['Volume'], [self.result])
        plt.ylabel('Volume')
        plt.ylim(bottom=0)

    def text_result(self):
        """
        Return the result of the problem as a string.
        """
        return f"Volume = {self.result}"

class ProblemSolverApp:
    def __init__(self, master, problem: Problem = RectangularVolumeProblem()):
        """
        Represents the GUI application for solving scientific problems.

        Parameters:
        - master: The Tkinter master window.
        - problem (Problem): An instance of the Problem class.
        """
        self.master = master
        self.master.title("Scientific Problem Solver")

        self.problem = problem

        # Set minimum window size
        self.master.minsize(width=800, height=500)

        self.create_widgets()

    def create_widgets(self):
        """
        Create and configure the GUI widgets.
        """
        # Set a light color scheme
        self.master.tk_setPalette(background='#FFFFFF', foreground='#000000', activeBackground='#EEEEEE', activeForeground='#000000')

        # Create a title label for the parameters section
        title_label = ttk.Label(self.master, text="Input Parameters", font=('Helvetica', 14, 'bold'),
                                background='#FFFFFF', foreground='#000000')
        title_label.grid(row=0, column=1, columnspan=2, pady=5, padx=10, sticky='n')

        # Create and place entry widgets with themed style
        style = ttk.Style()
        style.configure("TEntry", padding=(5, 2, 5, 2), font=('Helvetica', 12, 'bold'), fieldbackground='#FFFFFF', foreground='#000000')

        max_width = 200

        # Create labels and entry widgets based on problem parameters
        for i, (param_name, param_value) in enumerate(self.problem.parameters.items()):
            label = ttk.Label(self.master, text=f"{param_name.capitalize()}:", font=('Helvetica', 11, 'bold'), width=10,
                              background='#FFFFFF', foreground='#000000')
            label.grid(row=i+1, column=1, pady=1, padx=10, sticky='ne')

            entry = ttk.Entry(self.master, style="TEntry", width=10)  # Adjusted width
            entry.grid(row=i+1, column=2, pady=1, padx=10, sticky='n')
            entry.insert(0, param_value)  # Set default values

            setattr(self, f"{param_name}_entry", entry)

        # Create a button to submit the values with a themed style
        submit_button = ttk.Button(self.master, text="Submit", command=self.on_submit, style="TButton")
        submit_button.grid(row=len(self.problem.parameters)+2, column=1, columnspan=2, pady=10, sticky='n')

        # Calculate the number of parameters and adjust the figsize accordingly
        num_parameters = len(self.problem.parameters)
        plot_height = max(4, 0.5 * num_parameters)
        figsize = (max_width / 40, plot_height)

        # Create a Matplotlib figure and embed it in the Tkinter window
        fig, ax = plt.subplots(figsize=figsize, tight_layout=True)
        self.canvas = FigureCanvasTkAgg(fig, master=self.master)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(background='#FFFFFF')  # Set background color
        canvas_widget.grid(row=0, column=3, rowspan=len(self.problem.parameters)+3, pady=10, padx=10, sticky='nsew')

        # Create a Text widget to show the result under the plot
        self.result_text = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, height=5,
                                                     state=tk.DISABLED, background='#FFFFFF', foreground='#000000')
        self.result_text.grid(row=len(self.problem.parameters)+4, column=1, rowspan=1, columnspan=3, pady=5, padx=10, sticky='nwe')

        # Use grid_rowconfigure and grid_columnconfigure to make the rows and columns resizable
        self.master.grid_rowconfigure(0, weight=1)
        for i in range(len(self.problem.parameters)+1):
            self.master.grid_rowconfigure(i+1, weight=2)
        self.master.grid_rowconfigure(len(self.problem.parameters)+5, weight=1)

        # Adjust column weight for the last column to remove empty space on the right
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=2)
        self.master.grid_columnconfigure(2, weight=2)
        self.master.grid_columnconfigure(3, weight=12)
        self.master.grid_columnconfigure(4, weight=1)

    def on_submit(self):
        """
        Update the problem parameters and display the result.
        """
        try:
            # Update problem parameters based on entry values
            for param_name in self.problem.parameters.keys():
                entry_value = getattr(self, f"{param_name}_entry").get()
                self.problem.parameters[param_name] = float(entry_value)

            # Update the plot and result text
            self.update_plot_and_text()
        except ValueError:
            # Handle invalid input (non-numeric values)
            messagebox.showerror("Error", "Please enter valid numeric values for parameters")

    def update_plot_and_text(self):
        """
        Update the plot and result text based on the calculated result.
        """
        # Clear previous plot
        plt.clf()

        # Calculate result
        self.problem.calculate_result()

        # Create plot result
        self.problem.plot_result()

        # Update the canvas
        self.canvas.draw()

        # Update the result text
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, self.problem.text_result())
        self.result_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProblemSolverApp(root, RectangularVolumeProblem())
    root.mainloop()
