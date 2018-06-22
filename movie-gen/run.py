import fetch
import load

#f = fetch.Fetch()
#f.fetchdata()
#info = f.getinfo()

#l = load.Load(info[0], info[1], info[2], info[3], info[4], info[5], info[6], info[7], info[8])
l = load.Load("2013/06/16", "00:00:00", 12, 1, "SDO", "AIA", "AIA", 131, 12)
l.loadandgendata()
