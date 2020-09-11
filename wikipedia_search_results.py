#import wikipediaapi
import wikipedia
import csv

#expects an input csv and ouput csv

data = "agents.csv"
output = "wikioutput.csv"
#reads agents csv and provides the first matching url from wikipedia

def csvfile(data, output):
    #opens wikiput.csv to write wikiURLs to file
    with open(output, 'w', newline='') as outputFile:
        #adds header to file
        fieldnames = ['wikiURL1', 'wikiURL2']
        writer = csv.DictWriter(outputFile, fieldnames=fieldnames)
        writer.writeheader()
        #opens agents.csv to read data from
        with open(data, newline='') as data:
            reader = csv.DictReader(data)
            try:
                for row in reader:
                    #searches wikipedia for agents from agents.csv
                    search = wikipedia.search(str(row['agent']))
                    #returns first wikipedia page search result from agents csv
                    try:
                        page1 = wikipedia.page(search[0], auto_suggest=False)
                        page2 = wikipedia.page(search[1], auto_suggest=False)
                        #now you can use wikipedia api to easily get more info
                        print(page1.url)
                        print(page2.url)
                        #writes wiki URL to output csv file
                        writer.writerow({'wikiURL1': str(page1.url), 'wikiURL2': str(page2.url)})
                    except:
                        writer.writerow({'wikiURL1': "blank", 'wikiURL2': "blank"})
                        pass
            except:
                    pass

csvfile(data, output)
