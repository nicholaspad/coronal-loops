import re
import time

start_date = "2018/06/14"

def askendtime():
	r = re.compile("\d{4}/\d{2}/\d{2}")
	prompt = "Enter end date: (must be in format yyyy/mm/dd)\n==> "
	date = raw_input(prompt)
	if r.match(date) is None:
		print "Invalid date format."
		askendtime()
	else:
		if int(date[0:4]) >= int(start_date[0:4]) and int(date[5:7]) >= int(start_date[5:7]) and int(date[8:]) > int(start_date[8:]):
			end_date = date
		else:
			print "End date must be after start date."
			time.sleep(0.15)
			askendtime()
	askwavelength()

askendtime()
