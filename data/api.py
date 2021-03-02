from data.schema import *
from sqlalchemy import func
from sqlalchemy import distinct
import os

'''
   While this class is not the actual database, it is the API
   Contains methods for CRUD operation of the database
'''

class Database:
   '''
      
   '''
   def __init__(self, base, debug):
      self.base = base
      self.debug = debug
      print("Database started")

   '''
      Closes the database down
   '''
   def close(self):
      self.base.session.close()

   '''https://stackoverflow.com/questions/20743806/sqlalchemy-execute-return-resultproxy-as-tuple-not-dict/54753785
      Lucas Limas solution

      Executes raw SQL statements
      Only useful for SELECT statements
      returns them as a list of dicts
   '''
   def sqlSelect(self, statement):
      data = self.base.session.execute(statement).fetchall()
      results = []

      if len(data) == 0:
         return results

      for row_number, row in enumerate(data):
         results.append({})
         for column_number, value in enumerate(row):
            results[row_number][row.keys()[column_number]] = value

      return results

   '''
      Retrieves a list of all folders/paths in the database
   '''
   def getFolders(self):
      folders = [f.asDict() for f in Folders.query.all()]
      return folders

   '''
      Adds a new folder/path to the database
   '''
   def addPath(self, filePath):
      if Folders.query.filter_by(path=filePath).first() is None:
         newPath = Folders(path=filePath)
         self.base.session.add(newPath)
         self.base.session.commit()

   '''
      Removes a folder/path from the database
   '''
   def removePath(self, filePath):
      sql = "delete from folders where path=\"" + filePath + "\""
      self.base.session.execute(sql)
      self.base.session.commit()

   '''
      Sets all paths to be none active
   '''
   def setActivePath(self, filePath):
      #Sets all active folders/paths to non active
      sql1 = "update folders set active=0 where active=1"

      #Updates the passed path to be active
      sql2 = "update folders set active=1 where path=\""+ filePath+ "\""
      self.base.session.execute(sql1)
      self.base.session.execute(sql2)
      self.base.session.commit()

   '''
      Returns the selected active path if it exists
      Returns the string "None" if it doesnt exist
   '''
   def getActivePath(self):
      sql = "select path from Folders where active=1"
      query = self.base.session.execute(sql).scalar()

      if query:
         return query

      else:
         return "None"

   def getAllTagNames(self):
      sql = "select name from tag"

      return []

   ''' 
      Returns a dict in this format
      "standard" dict for the context of image values
      {
	      path: "",               | filepath to the image based on the folder  
	      tags: [],               | array of tags   
	      desc: "",               | short description, can be anything
	      rating: int,            | 
	      favorite: int
      }
      Returns data from database if its exsists, or substitutes default values if it doesnt
   '''
   def getImgDict(self, filename):
      sql1 = "select * from image where path=\"" + filename + "\"" #Gets image data matching filename
      #Gets tag names from association table for an image
      sql2 = "select name from tag inner join tags_association where tags_association.tag_id = tag.id and tags_association.image_id = " 

      try:
         count = self.sqlSelect("select count(*) from image where path =\"" + filename + "\"")
         count = count[0]["count(*)"]
         #If the image already exists
         if count == 1:
            d = self.sqlSelect(sql1)[0]
            d.update({"tags":[]})    
            d["tags"] = [t["name"] for t in self.sqlSelect(sql2 + str(d["id"]))]

         #First time image is loaded
         elif count < 1:
            d = {"path":filename, "tags":["no_tag"], "desc":"No description", "rating":0, "favorite":0}

         else:
            print("Something went wrong getting information for " + filename)
            d = {}

      except Exception as e:
         print("Could not retrieve image data error: " + str(e))
         d = {"path": filename, "tags":["no_tag"], "desc":"No description", "rating":0, "favorite":0}

      return d

   '''
      Checks for the existence of an image
      Adds the image if it doesnt exist
      Updates the image if it does exist based on standard dict
   '''
   def updateOrAddImage(self, imgDict):
      sql = "select * from image where path=\"" + imgDict["path"] + "\""
      result = self.sqlSelect(sql)
      if len(result) > 0:
         print("Updating image")
         #update desc
         #add new tags
         self.updateImgByDict(imgDict)

         print(result)
      else:
         print("Adding image")
         print(imgDict)
         self.addImgByDict(imgDict)
         self.updateImgByDict(imgDict)

   def addImgByDict(self, imgDict):
      img = Image(
         path = imgDict["path"],
         desc = imgDict["desc"]
      )
      self.base.session.add(img)
      self.base.session.commit()

   '''
      Updates data based on a passed json of the standard format
      Todo: DOES NOT REMOVE ASSOCIATION
   '''
   def updateImgByDict(self, imgDict):
      img = self.sqlSelect("select * from image where path = \"" + imgDict["path"] + "\"")[0]
      print(img)
      #Check for new tag entries
      tags = imgDict["tags"].split()
      for name in tags:
         self.checkTag(name)
      #Update tag associations
      self.base.session.commit()
      for name in tags: 
         #Create an association table
         self.checkAssociation(name, img["id"])
      
      #Update the description
      sql = "update image set desc=\"" + imgDict["desc"] + "\" where id=" + str(img["id"])
      self.base.session.execute(sql)
      self.base.session.commit()

   '''
      Checks for existence of association and adds if it doesnt exist
   '''
   def checkAssociation(self, tagName, i_id):
      sql1 = "select id from tag where name = \"" + tagName + "\""
      tagId = self.sqlSelect(sql1)[0]["id"]
      sql2 = "select count(*) from tags_association inner join tag where tags_association.tag_id = " + str(tagId) + " and tags_Association.image_id = " + str(i_id)
      count = self.sqlSelect(sql2)[0]["count(*)"]

      if count == 0:
         #ta = Tag_Association(tag_id = tagId, image_id=i_id)
         insert_ta = Tag_Association.insert().values(tag_id = tagId, image_id=i_id)
         self.base.session.execute(insert_ta)
         self.base.session.commit()

   '''
      Does NOT commit
      Checks for existence of a Tag and adds if it doesnt exist
   '''
   def checkTag(self, tagName):
      #Add the Tag if it doesnt exist
      count = self.sqlSelect("select count(*) from tag where name =\"" + tagName + "\"")
      if count[0]["count(*)"] < 1:
         self.base.session.add(Tag(name=tagName))
         self.base.session.commit()

   '''
      set1 = {1,2,3,4,5,6}
      set2 = {4,5,6,7,8,9}

      set1 intersect set2 = {4,5,6}
   '''
   def getImgListByTagStr(self, tagStr):
      tagList = tagStr.split()

      imgList = []
      selectList = {}
      if len(tagList) > 0:
         #Get the item list from the first tag
         sql = "select image.path from image, tags_association as tg, tag where tg.image_id = image.id and tg.tag_id = tag.id and tag.name = \"" + tagList[0] + "\""
         for t in tagList[1:]:
            #For every other tag, intersect it to the base
            sql = sql + " intersect select image.path from image, tags_association as tg, tag where tg.image_id = image.id and tg.tag_id = tag.id and tag.name = \"" + str(t) + "\""

         selectList = self.sqlSelect(sql)

      for d in selectList:
         imgList.append(d["path"])

      return imgList

   '''
      
   '''
   def getImageListByTag(self, tagName):
      #this needs to be modified to have ALL tags
      sql = "select image.path from image, tags_association as tg, tag where tg.image_id = image.id and tg.tag_id = tag.id and tag.name = \"" + str(tagName) + "\""
      selectList = self.sqlSelect(sql)
      imgList = []

      for d in selectList:
         imgList.append(d["path"])
      
      print("Returned imgList")
      print(imgList)
      return imgList

   '''  WARNING
      This executes and WILL commit raw sql queries

      Its used for the debug page
   '''
   def raw(self, sql):
      result = {}
      if(self.debug):
         try:
            first = sql.split()[0]
            print(first, " statement")
            if(first == "select"):
               result = self.sqlSelect(sql)

            elif sql != "":
               self.base.session.execute(sql)
               self.base.session.commit()
               result = {'result':'Executed a statement', 'statement': first}

         except Exception as e:
            result = { 'Input':sql, 'result': 'Error occured executing SQL', "error": str(e)}

      else:
         result = {'Error': 'Flask app is not being ran in development mode'}

      return result
