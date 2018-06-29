import fetch as f
import load as l

fe = f.Fetch()
fe.fetchdata()
info = fe.getinfo()

# time, period, interval, observatory, instrument, detector, measurement, fps
lo = l.Load(info[0], info[1], info[2], info[3], info[4], info[5], info[6], info[7])
lo.processdata()
