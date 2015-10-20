For indexing to be created and used we have to follow two steps:

1)Index usage:
	This is straight forward where we go to file where the class on databases is defined (In gstudio it is models.py) and below structures variable (where we define the various fields present along with their properties) we add another variable called indexes and list the fields on which we want to perform indexing.

For Example-

>>> class MyDoc(Document):
...     structure = {
...         'standard':unicode,
...         'other':{
...             'deep':unicode,
...         },
...         'notindexed':unicode,
...     }
...     
...     indexes = [
...         {
...             'fields':['standard', 'other.deep'],
...             'unique':True,
...         },
...     ]

	In versions before 0.7.1 of mongokit this simple addition would automatically create indexes for the data in mongoDB also. But in later versions this automatic index creation was removed (as people felt that indexes should be created with care directly on the collection). Gstudio uses Mongokit version 0.9.1.1 so this above addition only enables the database class to use the indexes if they are present in the database. We have to now manually create the indexes in mongoDB through mongo shell commands (This is infact told by mongokit as a deprecation warning that indexing is no longer automatic and we have to do it manually).

2)Index creation:
	We can actually use createIndex() command directly in mongoshell individually on various databases for required fields to create indexes. But it will reduce relocation, so we wrote the commands in a js file and then ran the script.

For Example-

test.js =>
	conn=new Mongo()
	db=conn.getDB("studio-dev")
	db.Nodes.createIndex({'_type':1,'name':1})
	//just keep adding these commands for creating Indexes in desired databases to required fields

$mongo<test.js  #written on the terminal

	As written in mongoDB documentation, it is preferable to use createIndex() rather than ensureIndex() command.

3)Index changes:
	In future if more fields are to be indexed, then we can append them to the js file (present in gnowsys-ndf folder as 'create_indexes_mongoshell.js') and run it again (Point 2)(if index is already present then the instruction does nothing) and also make necessary changes to the index variable present in the database class (models.py) (Point 1). If no indexing changes are done then running the script once will suffice.


	
