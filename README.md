## STA9760_Project1: Analyzing Millions of NYC Parking Violations

#### Goal: Load and analyze a dataset containing millions of NYC parking violations since January 2016
#### Dataset (OPVC API): https://dev.socrata.com/foundry/data.cityofnewyork.us/nc67-uf89
 

### Part 1: Python Scripting
#### Goal: 
- Develop a python command line interface that can connect to the OPCV API and demonstrate that the data is accessible via python. The python script must be able to run within docker but take parameters from the command line. It should also support having the option to print results out to a file.

#### Build Dockerfile:
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
  - How many times to request from the API. If not provided, will request data until the entirety of the content has been exhausted.
- Output: 
  - Optional. 
  - Write data to a json file. In not provided, will print results to stdout.

#### Command Line Arguments My Script Supports:
```
$ docker run -v ${pwd}:/app -e APP_KEY=${Your_APP_Key} -it nycproject:1.0 python -m main --page_size=1000 --num_pages=4 --output=results.json
```

#### Sample Output:
- Goal: It is expected that stdout or results.json will contain the API response, which is simply rows and rows of data from the API within the confines of the parameters provided to the script.
<img width="1311" alt="Sample Output" src="https://user-images.githubusercontent.com/60801548/77241266-f7e60e00-6bc5-11ea-87e6-fccb9fce8617.png">

### Part 2: Loading into ElasticSearch
#### Goal: 
- Leverage docker-compose to bring up a service that encapsulates nycproject container and an elasticsearch container and ensures that they are able to interact. The python script (from Part 1) now need not only download the data but also load it into the elasticsearch instance.

#### Build docker-compose.yml:
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
- Create Image:
```
$ docker-compose build pyth
```

- Launch ElasticSearch & Kibana:
```
$ docker-compose up -d
```

- Run Scripts:
  - Push 100,000 data to ElasticSearch
```
docker-compose run -e APP_KEY={YourAppKey} -v ${pwd}:/app/out= pyth python -m main --page_size=100 --num_pages=1000 --output=./out/results.json --push_elastic=True
```

- Navigate to http://localhost:9200/
  - Output:
<img width="453" alt="9200" src="https://user-images.githubusercontent.com/60801548/77241836-3da6d480-6bce-11ea-8350-438d126091b3.png">

- Run curl request and save output.txt File:
```
curl -o output.txt http://localhost:9200/nycproject/_search?q=state:NY&size=10
```
  - View in Browser:
```
http://localhost:9200/nycproject/_search?q=state:NY&size=2
```
  - Sample Output
<img width="1319" alt="output" src="https://user-images.githubusercontent.com/60801548/77241881-17356900-6bcf-11ea-909b-9f8eca0ce7f9.png">


### Part 3: Visualizing and Analysis on Kibana

#### Goal: 
- Stand up an instance of Kibana on top of the ElasticSearch instance in order to visualize and analyze dataset. Create visualizations in Kibana that analyze the data loaded and presents analysis in graphical form. 

- Navigate to http://localhost:5601/

- Load Past 5 Years Data:
<img width="1316" alt="5 years" src="https://user-images.githubusercontent.com/60801548/77241947-d722b600-6bcf-11ea-88c4-e66819d36866.png">

#### Visualize Dataset
- Vertical Bar Chart - Which county had the highest average reduction amount?

<img width="1442" alt="Vertical Bar Chart" src="https://user-images.githubusercontent.com/60801548/77241984-28cb4080-6bd0-11ea-8e9f-d996238758f0.png">

- Horizontal Bar Chart - Which violation was most popular? Second most popular? 
<img width="1442" alt="Horizontal Bar Chart" src="https://user-images.githubusercontent.com/60801548/77242018-81024280-6bd0-11ea-9f41-df4eef1a873d.png">

- Pie Chart - What are the top 5 violation type? Pencentages?
<img width="1439" alt="Pie Chart" src="https://user-images.githubusercontent.com/60801548/77242062-f0783200-6bd0-11ea-85dd-fa7dccd3af8e.png">

- Line Chart - What are the monthly changes of Fine Amount, Interest Amount, and Penalty Amount?
<img width="1437" alt="Line Chart" src="https://user-images.githubusercontent.com/60801548/77242082-24535780-6bd1-11ea-8493-27cc190ef4cb.png">

- Metric - How many cases occred for the top 10 types of violations?
<img width="1443" alt="Metric" src="https://user-images.githubusercontent.com/60801548/77242096-4d73e800-6bd1-11ea-9dc8-4d4bfc0d1471.png">

- Create a Dashboard
<img width="1437" alt="Dashboard" src="https://user-images.githubusercontent.com/60801548/77242101-595faa00-6bd1-11ea-9bb3-56a4b72f5aed.png">
