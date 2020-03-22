from sodapy import Socrata
from src.nycproject.elasticsearch import create_and_update_index, push_data

def get_nycdata(app_key,page_size,num_pages,push_elastic):
	results = []
	client = Socrata("data.cityofnewyork.us",app_key)
	count_rows = int(client.get('nc67-uf89', select='COUNT(*)')[0]['COUNT'])

	if not num_pages:
		num_pages = count_rows//page_size+1

	if push_elastic:
		es = create_and_update_index('nycproject')

	for i in range(0,num_pages):
		data_collect = client.get('nc67-uf89',limit=page_size,offset=i*(page_size))
		results.append(data_collect)
		for data in data_collect:
			if push_elastic:
				push_data(data,es,'nycproject')

	return results 