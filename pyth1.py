#!/usr/bin/env python3
import time
import http.client
from concurrent.futures import ThreadPoolExecutor

# creates a list of values as long as the number of things we want
# in parallel so we could associate an ID to each. More parallelism here.
parallel = 20
runs=[value for value in range(parallel)]
mean=0.56
std=1.7
count = 1000

def getpage(id):
    try:
        host = "ghxbycdfza.execute-api.us-east-1.amazonaws.com"
        c = http.client.HTTPSConnection(host)
        json= '{ "key1": '+str(mean)+',"key2":'+str(std)+',"key3":'+str(count)+'}'
        c.request("POST", "/default/testFunction", json)

        response = c.getresponse()
        data = response.read().decode('utf-8')
        conv=data.split(",")
        var95=float(conv[0][1:])
        var99=float(conv[1][:-1])
        
        print( var95,var99, " from Thread", id )
    except IOError:
        print( 'Failed to open ', host ) # Is the Lambda address correct?
    print(data+" from "+str(id)) # May expose threads as completing in a different order
    return "page "+str(id)

def getpages():
    with ThreadPoolExecutor() as executor:
        results=executor.map(getpage, runs)
    return results

if __name__ == '__main__':
    start = time.time()
    results = getpages()
    print( "Elapsed Time: ", time.time() - start)
    #for result in results:  # uncomment to see results in ID order
    #     print(result)
