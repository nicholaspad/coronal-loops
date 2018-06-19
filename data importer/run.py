import fetcher as fet
import downloader as dow

fe = fet.Fetcher()
fe.fetchdata()

dl = dow.Downloader(fe.getsearchresults())
dl.pipedata()
