from nsetools import Nse

class stockDetails:
    def stockData(request):
        nse = Nse
        q = nse.get_index_list()
        print(q)