import gen
import fetch
import load

f = fetch.Fetch()
f.fetchdata()
info = f.getinfo()

l = load.Load(info[0], info[1], info[2], info[3], info[4], info[5], info[6], info[7])
# l = load.Load("2017/08/08", "00:00:00", 200, 1, "SDO", "AIA", "AIA", 171)
l.loaddata()

g = gen.Gen("output.mp4", info[8])
# g = gen.Gen("output.mp4", 20)
g.process()
