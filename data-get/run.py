import search as s
import load as l

se = s.Search()
se.go()

lo = l.Load(se.getsearch())
lo.go()
