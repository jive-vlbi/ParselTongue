try:
    import urllib.request as ul		# Python 3
except:
    import urllib as ul			# Python 2

def urlretrieve(url, file):
    return ul.urlretrieve(url, file)
