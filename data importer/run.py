import importer as imp
import fetcher as fet
import downloader as dow

fe = fet.Fetcher()
fe.fetchdata()

dl = dow.Downloader(fe.getsearchresults())
dl.pipedata()

# ip = imp.Importer()
# ip.importlist()




"""
TODO
- way to retrieve data from online
- hook into pyplot and sunpy in order to generate image from a user-inputted datapoint (filename)
- show multiple images?
- upon closing the window, prompt user for another file opening
- FINAL: figure out how to generate a movie using the files
"""
