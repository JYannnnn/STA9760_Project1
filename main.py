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