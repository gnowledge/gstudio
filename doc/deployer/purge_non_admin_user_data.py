from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.models.node import Node
from gnowsys_ndf.ndf.views.methods import delete_node

def test_data():
	activity_pages_creator = node_collection.find({'_type': 'GSystem', 'member_of': Node.get_name_id_from_type('')})

def main():
	test_data()
	# [ p.name for p  in node_collection.find({'_type': 'GSystem', 'created_by': {'$in': activity_pages_creator.distinct('created_by') }, 'member_of': Node.get_name_id_from_type('Page', 'GSystemType')[1] }) ] 
                                                                               


if __name__ == '__main__':
	main()
