## STA9760_Project1: Analyzing Millions of NYC Parking Violations

### Part 1: Python Scripting

#### Build Dockerfile
```
FROM python:3.7 

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt
```
#### Packages:
```
certifi==2019.11.28
chardet==3.0.4
idna==2.9
requests==2.23.0
sodapy==2.0.0
urllib3==1.25.8
```

#### Library: 
- sodapy

#### Key Arguments:
- App_Key: 
  - Make sure that user can pass along an App_Key for the API in a safe manner
- Page_Size: 
  - Required. 
  - How many records to request from the API per call.
- Num_Pages: 
  - Optional. 
  - How many pages to request from the API per call. If not provided, will request data until the entirety of the content has been exhausted.
- Output: 
  - Optional. 
  - Write data to a json file. In not provided, will print results to stdout.

#### Command Line Arguments my script support:
```
$ docker run -e APP_KEY={YOUR_APP_KEY} -t bigdata1:1.0 python main.py --page_size=1000 --num_pages=4 --output=results.json
```

#### Sample Output:
<img width="1311" alt="Sample Output" src="https://user-images.githubusercontent.com/60801548/77241266-f7e60e00-6bc5-11ea-87e6-fccb9fce8617.png">

### Part 2: Loading into ElasticSearch

#### Build docker-compose.yml
```
version: '3'
services:
  pyth:
    network_mode: host
    container_name: pyth
    build:
      context: .
    volumes:
      - .:/app:rw 
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:6.3.2
    environment: 
      - cluster.name=docker-cluster
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    ports:
      - "9200:9200"
  kibana:
    image: docker.elastic.co/kibana/kibana:6.3.2
    ports:
      - "5601:5601"
```
#### Packages:
```
certifi==2019.11.28
chardet==3.0.4
idna==2.9
requests==2.23.0
sodapy==2.0.0
urllib3==1.25.8
elasticsearch==7.5.1
```

#### Library: 
- elasticsearch

#### Scripts:
- `main.py`
```
import os
import argparse

from src.nycproject.api import get_nycdata

#if directly call, run the below codes
if __name__ == "__main__":
	app_key = os.getenv(f'APP_KEY')

	parser = argparse.ArgumentParser()
	parser.add_argument("--page_size", type=int)
	parser.add_argument("--num_pages", default=None, type=int)
	parser.add_argument("--output", default=None)
	parser.add_argument("--push_elastic", default=False, type=bool)
	args = parser.parse_args()

	#define nycdata using get_nycdata function
	nycdata = get_nycdata(app_key,args.page_size,args.num_pages,args.push_elastic)

	#write output file
	with open(args.output,"w") as outfile:
		for lines in nycdata:
			for line in lines:
				outfile.write(f"{line}"+'\n')
```

- `elasticsearch.py`
```
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
```

- `api.py`
```
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
```

#### Elastic Search:
- Create Image from Base to Our Layer:
```
$ docker-compose build pyth
```

- Run ElasticSearch & Kibana:
```
$ docker-compose up -d
```

- Run Scripts:
  - Push 100,000 data to ElasticSearch
```
docker-compose run -e APP_KEY={YourAppKey} -v ${pwd}:/app/out= pyth python -m main --page_size=100 --num_pages=1000 --output=./out/results.json --push_elastic=True
```

- Navigate to http://localhost:9200/
<img width="453" alt="9200" src="https://user-images.githubusercontent.com/60801548/77241836-3da6d480-6bce-11ea-8350-438d126091b3.png">

- Run curl request:
  - Save output.txt File
```
curl -o output.txt http://localhost:9200/nycproject/_search?q=state:NY&size=10
```
  - View in Browser
```
http://localhost:9200/nycproject/_search?q=state:NY&size=2
```
  - Sample Output
<img width="1319" alt="output" src="https://user-images.githubusercontent.com/60801548/77241881-17356900-6bcf-11ea-909b-9f8eca0ce7f9.png">


 
