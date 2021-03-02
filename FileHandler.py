import os
from os.path import isfile, join
'''
    This object handles the parsing and image file handling done by the app
    Everything here is returned as lists of file names or strings

    Can't get a neat way to see local files, so this thing will also help by returning paths

    Things this object does:
        Keeps current directory saved
        Returns current directory
        Fetches file and folder names in directory
        Possibly renames files in a directory
            If the file has database information for example will add a "db_" prefix or something
        Scans folder for new (non database) files
'''


'''
    Takes in a Database reference      
'''
class FileHandler:
    def __init__(self, db_context):
        self.DB = db_context
        self.directory = self.DB.getActivePath()
        self.savedPaths = self.DB.getFolders()
    
    def setActiveDir(self, dir):
        if dir == "None":
            self.directory = ""
        else:
            self.directory = dir

    def viewFilesInFolder(self):
        if self.directory:
            return [f for f in os.listdir(self.directory) if isfile(join(self.directory, f))]
        else:
            print("FH directory is None")
            return [""]

    def getDir(self):
        return self.directory

    def removePath(self, dir):
        if self.directory == dir:
            self.directory = ""