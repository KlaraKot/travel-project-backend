#algorytm do wyliczania średniej wartości oceny miasta
import pandas as pd
import pymongo
from myapp import models

def convertToCSV():

    myclient = pymongo.MongoClient("mongodb+srv://Zuzanna:bxMZHt0wKUQlx9yn@kalejdoskop.bjapu.mongodb.net/Kalejdoskop?retryWrites=true&w=majority")
    db = myclient["TestMigracji"]

    col1 = db["myapp_city"]
    col2 = db['myapp_cityrate']

    cursor1 = col1.find()
    cursor2 = col2.find()

    mongo_docs1 = list(cursor1)
    mongo_docs2 = list(cursor2)

    docs1 = pd.DataFrame(columns=['cityName', 'country', 'description', 'monuments', 'averageRate'])
    docs2 = pd.DataFrame(columns=['cityName', 'rate', 'userId'])

    for num, doc in enumerate( mongo_docs1):
        doc["cityName"] = str(doc["cityName"])
        doc_name = doc["cityName"]
        series_obj = pd.Series(doc, name=doc_name)
        docs1 = docs1.append(series_obj)

    for num, doc in enumerate( mongo_docs2):
        doc["cityName"] = str(doc["cityName"])
        doc_name = doc["cityName"]
        series_obj = pd.Series(doc, name=doc_name)
        docs2 = docs2.append(series_obj)

    csv_export = docs1.to_csv(sep=',')
    csv_export = docs2.to_csv(sep=',')

    docs1.to_csv("cities.csv", index=False)
    docs2.to_csv("rates.csv", index=False)




def averageRate():
    convertToCSV()
    metadata = pd.read_csv('./rates.csv', low_memory=False);

    value = metadata['rate']
    cityName = metadata['cityName']

    cities = {}
    Sum = {}

    for i in range(len(cityName)):
        if cityName[i] in cities:
             cities[cityName[i]] += 1
             Sum[(cityName[i])] += value[i]
        else:
            cities[cityName[i]] = 1
            Sum[(cityName[i])] = value[i]


    average = {}

    for c in cities:
        average[c] = Sum[c]/cities[c]
    
    print(average)
    return average


def averageRateToCity():

    average = {}
    average = averageRate() 
    cities = models.City.objects.all()
    
    for city in cities:
        if city.cityName in average:
            city.averageRate = average[city.cityName]
            print(city.cityName)
            print(city.averageRate)

            c2 = models.City(id=city.id, cityName=city.cityName, country=city.country,
            description=city.description, monuments=city.monuments, averageRate=average[city.cityName])
            
            #city.delete()
            c2.save()

    


def tenBestRated():
    convertToCSV()
    metadataPlaces = pd.read_csv('./cities.csv', low_memory=False)
    metadataRate = pd.read_csv('./rates.csv', low_memory=False)
    value = metadataPlaces['averageRate']
    ratersD = {}
    cityNames = metadataRate['cityName']

    for c in cityNames:
        if c in ratersD:
            ratersD[c] += 1
        else:
            ratersD[c] = 1

    raters = []
    cities = metadataPlaces['cityName']

    for c in cities:
        if c in ratersD:
            raters.append(ratersD[c])
        else:
            raters.append(0)

    C = sum(value)/len(value)
    
    ratersSeries = pd.Series(raters)
    
    metadataPlaces = metadataPlaces.assign(raters = ratersSeries)
    m = metadataPlaces['raters'].quantile(0.90)
    
    q_places = metadataPlaces.copy().loc[metadataPlaces['raters'] >= m]

    def weighted_rating(x, m=m, C=C):
        v = x['raters']
        R = x['averageRate']
        return (v/(v+m) * R) + (m/(m+v) * C)
    
    q_places['score'] = q_places.apply(weighted_rating, axis=1)
    q_places = q_places.sort_values('score', ascending=False)
    
    return q_places.head(10)




