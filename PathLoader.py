from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os

Tk().withdraw()
dir = '//*/home/JOBS'
filename = str(askopenfilename(initialdir=dir))
copy = filename.split('JOBS/', 1)[1].replace('&', '^^^&')
print(copy)
os.system("echo %s | clip" % copy)

