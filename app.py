from flask import Flask, render_template, send_from_directory, json, request
import os
import socket
import logging
from data.api import Database
from data.schema import db as Base
from FileHandler import FileHandler

"""
   This is a tool for categorizing images and videos within a specific folder
   It will allow a user to add tags of their own creation to each file
   They can then search for tags and the application will retrieve them

   Bandwidth isnt a concern with this project. It is not designed to be used outside a local network

   installation:
   python 3.9.1 64bit
   pip
   pip install flask
   pip PIL still installed?
   pip install flask-sqlalchemy
"""
app = Flask(__name__, 
            static_url_path="",
            template_folder="templates")

debugMode = True

#Turns off GET response spam in console
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

#Database setup
#dbName = "databasename" + getDBnumber(app.root_path) +".db"
dbName = "info.db"
app.config.update(dict(
                        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(app.root_path + "/data", dbName),
                        SQLALCHEMY_TRACK_MODIFICATIONS=False))

Base.init_app(app)
app.app_context().push()
Base.create_all()
DB = Database(Base, debugMode)
FH = FileHandler(DB)

#List of specific phrases which can be used
phraseMap = {
   "View Files" : FH.viewFilesInFolder,
   "View Paths" : DB.getFolders
}

def main():
   app.debug = debugMode

   #This block of code figures out what the local IP is of the server
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.connect(("8.8.8.8", 80))
   print("\nLocally connect by going to this address: " + s.getsockname()[0] + ":5000\n")
   s.close()

   app.run(host="0.0.0.0")

############################## Routing #######################################
#                    Returns templates for the user


###############################################
#  Index page
#  Passes a set of file names as an array
#  
###############################################
@app.route("/")
@app.route("/index")
def getIndex():
   extensions = (".jpg", ".png", ".gif", ".webp", ".tiff", ".psd", ".raw", ".bmp", ".heif", ".indd")
   tags = request.args.get("tags")
   page = request.args.get("page")
   imgNameList = []
   
   if page is None:
      page=0

   if tags is not None:
      imgNameList = DB.getImgListByTagStr(tags)

   #Grabs all file names in the current directory with the specified extensions
   elif FH.getDir() != "None":
      for filename in os.listdir(FH.getDir()):
         if filename.endswith(extensions):
            imgNameList.append(filename)

   return render_template("index.html", imgNames=imgNameList, pagenumber=page)
   
###############################################
#  Returns showImage template
#  Displays an image in a responsive way
###############################################
@app.route("/image/<filename>")
def showImage(filename):
   data = DB.getImgDict(filename)
   return render_template("image.html", img=filename, data=data)


###############################################
#  Only in developmental version
#
#  Switches between two different directories
#     for "reasons"
#  
#  Once added, a directory manager will replace this
###############################################
@app.route("/config")
def config():
   data = {"Folders":[], "Tags":[]}
   data["Folders"] = DB.getFolders()
   data["Tags"] = DB.getAllTagNames()

   return render_template("config.html", data=data)


###############################################
#  Only in developmental version
#
#  A bunch of forms for testing the database
#  Unaccessible outside of debug mode
###############################################
@app.route("/db")
def databaseAPI():
   if(debugMode):
      data = [{"empty string" : "Hi"}]

      txt = request.args.get("search")
      if txt!= "":
         data = parse(txt)

      return render_template("dbtest.html", data=data, phrases=list(phraseMap.keys()))
   else:
      return render_template("404.html")

############################## API and Other Routing #######################################
#              Automatic requests, errors, tools
###############################################
#  Returns an image given a specified filename
#  ex:     /getimage/tulips.png
#  Used as the src attribute for the img element
###############################################
@app.route("/getimage/<filename>")
def getImage(filename):
   return send_from_directory(FH.getDir(), filename)

###############################################
#  Takes in a JSON and udpates an image with it
#  
#  
###############################################
@app.route("/imagedata", methods=["POST"])
def updateImage():
   j = request.json
   DB.updateOrAddImage(j)
   return "200"

@app.route("/path/<path:filePath>", methods=["POST"])
def createPath(filePath):
   delete = request.args.get("delete")
   active = request.args.get("active")

   if delete == "true":
      DB.removePath(filePath)
      FH.removePath(filePath)
   
   elif active=="true":
      DB.setActivePath(filePath)
      FH.setActiveDir(filePath)

   else:
      DB.addPath(filePath)

   return config()

###############################################
#  When this route is accessed the server will be shut down
#
###############################################
@app.route("/shutdown", methods=["GET", "POST"])
def shutDownServer():
   if request.method == "POST":
      func = request.environ.get("werkzeug.server.shutdown")
      if func is None:
         raise RuntimeError("Not running with the Wekzeug Server")
      DB.close()
      func()
      return "Categorizationer has shut down..."

   return render_template("shutdown.html")

###############################################
#  Page not found 404 error
#  Returns 404 template
###############################################
@app.errorhandler(404)
def pageNotFound(e):
   return render_template("404.html")

###############################################
#  Returns a video given a specified filename
#  ex:     /getvideo/tulips.mp4
#  Used as the src attribute for the video element
###############################################
@app.route("/video")
def getVideo():
   return "Video object"

############################## Development tools #######################################
#              Supposedly stop caching so I can refresh new CSS
@app.after_request
def afterRequest(response):
  response.headers["Cache-Control"] = "no-store"
  return response

############################## General tools #######################################
def parse(input):
   if input in phraseMap:
      return phraseMap[input]()  #Don't forget parenthesis

   else: #Suspect input is raw SQL
      return DB.raw(input)

############################## App run #######################################


if __name__ == '__main__':
   main()
   