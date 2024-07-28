from tkinter import *
from tkinter import ttk
from ttkthemes import ThemedTk
from BuzzWebScrapping import BuzzWebScrapping

def save_credentials():
    js = str({"email": e1.get(), "password": e2.get()}).replace("'", '"')
    api = str({'googlekey': e3.get()}).replace("'", '"')

    with open("./data/buzz_monitor.json", "w") as f:
        f.write(str(js))

    with open('./data/gemini.json', 'w') as f:
        f.write(str(api))

def execute_scrappy():
    bz = BuzzWebScrapping()
    bz.run()

def close_program():
    root.quit()

if __name__ == '__main__':
    root = ThemedTk(theme="plastik")
    root.title("BuzzAI")

    # Configurar estilo
    style = ttk.Style()
    style.configure('TLabel', font=('Helvetica', 12))
    style.configure('TButton', font=('Helvetica', 12), padding=10)
    style.configure('TEntry', font=('Helvetica', 12))

    mainframe = ttk.Frame(root, padding="20 20 20 20")
    mainframe.grid(row=0, column=0, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    title_label = ttk.Label(mainframe, text='BuzzAI', font=('Helvetica', 16, 'bold'))
    title_label.grid(row=0, column=0, columnspan=2, pady=10)

    ttk.Label(mainframe, text='Buzz Email').grid(row=1, column=0, pady=5, sticky=E)
    ttk.Label(mainframe, text='Buzz Password').grid(row=2, column=0, pady=5, sticky=E)
    ttk.Label(mainframe, text='Google API Key').grid(row=3, column=0, pady=5, sticky=E)

    e1 = ttk.Entry(mainframe, width=25)
    e2 = ttk.Entry(mainframe, width=25, show='*')
    e3 = ttk.Entry(mainframe, width=25)

    e1.grid(row=1, column=1, padx=5, pady=5)
    e2.grid(row=2, column=1, padx=5, pady=5)
    e3.grid(row=3, column=1, padx=5, pady=5)

    button = ttk.Button(mainframe, text="Save Credentials", command=save_credentials)
    button.grid(row=4, column=0, columnspan=2, pady=10)

    newbutton = ttk.Button(mainframe, text="Execute Process", command=execute_scrappy)
    newbutton.grid(row=5, column=0, columnspan=2, pady=10)

    close_button = ttk.Button(mainframe, text="Close Program", command=close_program)
    close_button.grid(row=6, column=0, columnspan=2, pady=10)

    root.mainloop()
