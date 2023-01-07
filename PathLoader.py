# All the script does is open a window that lets a user click on a job file and have the file path from a certain directory copied to the clipboard.
# This is absolutely a hack, but we used the file path as the job title stored in our job databases.
# This script eliminated the chance that the path would be entered incorrectly and was the foundation of every automation we enacted after that. 

from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os

Tk().withdraw()
dir = '//*/home/JOBS'
filename = str(askopenfilename(initialdir=dir))
copy = filename.split('JOBS/', 1)[1].replace('&', '^^^&')
print(copy)
os.system("echo %s | clip" % copy)

