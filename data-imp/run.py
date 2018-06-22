import fetcher as fet
import downloader as dow

fe = fet.Fetcher()
fe.fetch()

dl = dow.Downloader(fe.getsearch())
dl.pipe()
