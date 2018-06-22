import fetch
import load

f = fetch.Fetch()
f.fetchdata()
info = f.getinfo()

# time, period, interval, observatory, instrument, detector, measurement, fps
l = load.Load(info[0], info[1], info[2], info[3], info[4], info[5], info[6], info[7])
l.processdata()
