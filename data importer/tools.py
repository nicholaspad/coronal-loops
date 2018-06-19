import sys

def bar(count, total, status):
		# includes code from https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
		bar_len = 60
		filled_len = int(round(bar_len * count / float(total)))
		percent = round(100.0 * count / float(total), 1)
		bar = "=" * filled_len + "-" * (bar_len - filled_len)
		if count != 100:
			sys.stdout.write("\r[%s] %s%s ...%s\r" % (bar, percent, "%", status))
		else:
			sys.stdout.write("[%s] %s%s ...%s\n" % (bar, percent, "%", status))
		sys.stdout.flush()

def parsemonth(num):
	months = {
		1 : "Jan.",
		2 : "Feb.",
		3 : "March",
		4 : "Apr.",
		5 : "May",
		6 : "June",
		7 : "July",
		8 : "Aug.",
		9 : "Sept.",
		10 : "Oct.",
		11 : "Nov.",
		12 : "Dec."
	}
	return months[num]
