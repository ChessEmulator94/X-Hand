import tkinter as tk
from Screens import Screen1, Screen2


text_colour = "#c6c9c3"
button_colour = "#335145"

class windows(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        w = 1200
        h = 800
        self.geometry(f"{w}x{h}")

        container = tk.Frame(self, height=800, width=1200)
        container.config(bg="#646e78")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (Screen1, Screen2):
            frame = F(container, self)

            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Screen1)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


def main():
    testObj = windows()
    testObj.mainloop()

if __name__ == "__main__":
    main()
