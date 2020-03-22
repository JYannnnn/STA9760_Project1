from datetime import datetime, date
from elasticsearch import Elasticsearch

#Create index
def create_and_update_index(index_name):
    #Connect to localhost by default
    es = Elasticsearch()
    try:
        es.indices.create(index=index_name)
    except:
        pass
    return es

#Change data formatting for amount and date
def formatting(data):
    for key, value in data.items():
        if 'amount' in key:
            data[key] = float(value)
        elif 'date' in key:
            try:
                data[key] = datetime.strptime(data[key], '%m/%d/%Y').date()
            except:
                pass
                  
#Push data to Elastic Search
#Use 'summons_number' as unique id
def push_data(data, es, index):
    formatting(data)
    res = es.index(index=index, body=data, id=data['summons_number'])