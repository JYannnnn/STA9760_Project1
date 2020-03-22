## STA9760_Project1: Analyzing Millions of NYC Parking Violations

### Part 1: Python Scripting
#### Packages:
- certifi==2019.11.28
- chardet==3.0.4
- idna==2.9
- requests==2.23.0
- sodapy==2.0.0
- urllib3==1.25.8

#### Key Arguments:
- App_Key: Make sure that user can pass along an App_Key for the API in a safe manner
- Page_Size: Required. How many records to request from the API per call.
- Num_Pages: Optional. How many pages to request from the API per call. If not provided, will request data until the entirety of the content has been exhausted.
- Output: Optional. Write data to a json file. In not provided, will print results to stdout.

