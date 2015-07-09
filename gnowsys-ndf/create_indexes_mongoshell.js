/*run this file from the terminal by typing the command mongo<creating_indexes_mongoshell.js this will run the script and create indexes on the below fields and when ever u want to include new fields make the update in the respective class in /gnowsys-ndf/ndf/models.py and include it in this file*/

conn=new Mongo();
db=conn.getDB("studio-dev");
db.Nodes.createIndex({'_type':1,'name':1})
db.Nodes.createIndex({'_type':1,'_id':1})
//db.Nodes.createIndex({'content':1})
//db.Nodes.createIndex({'tags':1})
//db.Nodes.createIndex({'status':1})
//db.Nodes.createIndex({'collection_set':1})
//db.Nodes.createIndex({'type_of':1})
//db.Nodes.createIndex({'member_of':1})
//db.Nodes.createIndex({'attribute_set':1})
//db.Nodes.createIndex({'relation_set':1})
db.Triples.createIndex({'_type':1,'name':1})
//db.Triples.createIndex({'object_value':1})
//db.Triples.createIndex({'status':1})
//db.Triples.createIndex({'right_subject':1})
db.Triples.createIndex({'_type':1,'subject':1,'atribute_type':1})
db.Triples.createIndex({'_type':1,'subject':1,'relation_type':1})
db.Nodes.createIndex({'member_of':1,'status':1,'last_update':1})
