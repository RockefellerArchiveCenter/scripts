import pywikibot
import csv

#expects an input csv and ouput csv
#requires configfile
data = "agents.csv"
output = "wikidataoutput.csv"
#reads agents csv and returns wikipedia page and wikidata ItemPage object

def csvfile(data, output):
    with open(output, 'w', newline='') as outputFile:
        fieldnames = ['page', 'item']
        writer = csv.DictWriter(outputFile, fieldnames=fieldnames)
        writer.writeheader()
        with open(data, newline='') as data:
            reader = csv.DictReader(data)
            try:
                site = pywikibot.Site("en", "wikipedia")
                for row in reader:
                    try:
                        print((str(row["agent"])))
                        page = pywikibot.Page(site, str(row["agent"]))
                        item = pywikibot.ItemPage.fromPage(page)
                        print(page)
                        print(item)
                        writer.writerow({'page': str(page), 'item': str(item)})
                    except:
                        writer.writerow({'page': "blank"})
                        pass
            except:
                    pass

csvfile(data, output)
