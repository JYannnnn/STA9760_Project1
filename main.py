import sys
import os

from src.nycproject.api import get_nycdata

#if directly call, run the below codes
if __name__ == "__main__":
	print(sys.argv)

	#skip the first value
	args = sys.argv[1:]
	print(args)

	#get and print the value of 'APP_KEY' environment variable 
	app_key = os.getenv(f'APP_KEY')
	print(app_key)

	#define page_size, num_pages, and output
	page_size = int(args[0])
	num_pages = int(args[1])
	output = args[2]

	#define and print nycdata using get_nycdata function
	nycdata = get_nycdata(app_key,page_size,num_pages)
	print(nycdata)

	#write output file
	with open(output,"w") as outfile:
		for lines in nycdata:
			for line in lines:
				outfile.write(f"{line}"+'\n')