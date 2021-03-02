from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy

'''
https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html

    ImageData    Image   Tag  Folders
        #          #     #
        ->Image     -> <-
                     Tags
                      #
An Image for each picture in the folder
Each Image gets a 1-to-1 ImageData
Each Image gets a Many-to-Many Tag

A Tag for each user generated tag
Each tag gets a Many-to-Many Image

A folder for every root folder the program uses

'''

db = SQLAlchemy()

'''
    A many to many associative table for images to tags
'''
Tag_Association = db.Table("tags_association",
                db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
                db.Column("image_id", db.Integer, db.ForeignKey("image.id"), primary_key=True)
)

'''
    A unique tag which can be associated with an item

    id - primary key
        unique identifier used interally

    name - Actual tag name (ie: car, red, sitting)
    images - Associative table
'''
class Tag(db.Model):
    __tablename__ =  "tag"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))

    def asDict(self):
        return{c.name: getattr(self, c.name) for c in self.__table__.columns}

'''
    An image entry which holds the path to an image and its relationships 

    id - primary key
        unique identifier used interally
    
    path - Actual path to the image from selected parent folder
    data - one-to-one table to an images custom data
    tags - Associative table
'''
class Image(db.Model):
    __tablename__ =  "image"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String(100))
    tags = db.relationship("Tag", secondary=Tag_Association, backref=db.backref("images")) #backref - Gets set of images using a tag?
    desc = db.Column(db.String(200))

class Folders(db.Model):
    __tablename__ = "folders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String(100))    #might need to be longer
    active = db.Column(db.Boolean, default=False)

    def asDict(self):
        return{c.name: getattr(self, c.name) for c in self.__table__.columns}
