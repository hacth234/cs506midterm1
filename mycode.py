import pandas as pd
import requests
import numpy
import geopandas as gpd
import csv
from geopandas import GeoSeries
from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.ops import nearest_points

def add_census_tract(dataframe):
   polygons = gpd.read_file("data/tl_2019_25_tract/tl_2019_25_tract.shp")
   polygons = polygons.rename(columns={"TRACTCE": "census_tract"}, index=str)
   polygons = polygons.to_crs("EPSG:26986")
   gdf = dataframe
   df = gpd.sjoin(gdf, polygons[['census_tract', 'geometry']], how='left', op='within')
   df.drop(columns=['index_right'], inplace=True)
   return df

def get_median_hh_income():
        '''
            Returns Pandas DataFrame representation Median Household Income Estimate by Census Tract for MA.
            American Community Survey (ACS) 2018 Census data used.
            Specific table: ACS 2018 5-year detailed table "B19013_001E"
        '''
        URL = "https://api.census.gov/data/2018/acs/acs5?get=B19013_001E&for=tract:*&in=state:25"
    
        response = requests.get(url = URL)
        data = response.json()
        
        median_income_df = pd.DataFrame(data[1:len(data)-1], columns = data[0])
        return median_income_df


#uses 0.5 miles as a metric to get the area around the stop
#
def encompassingArea(lat, long):
    return 0
#point is latitude and longitude of the stop, Xset is the income levels
#Xset is a numpyarray for parts of boston area with latitude, longitude, MedianAverageHouseHoldIncome, EstRadius
def assignStopToMedianIncome(point, Xset, radius):
    avgIncome = 0
    incomesAssigned = []
    vb = len(Xset)
    #print(vb)
    ct = 0
    for x in range(vb):
        #print(Xset[x])
        #lat1 = point[0]
        #long1 = point[1]
        lat2 = float(Xset[x][1])
        long2 = float(Xset[x][2])
        #print(lat2, long2)
        incomeXset = float(Xset[x][3])
        radiusXset = float(Xset[x][4])
        pointA = point
        pointB = (lat2, long2)
        if (isCircleIntersect(pointA, pointB, radius, radiusXset)):
            incomesAssigned.append(incomeXset)
            #ct +=1
            #print(ct)
    for x in range(len(incomesAssigned)):
        avgIncome = avgIncome + incomesAssigned[x]
    if len(incomesAssigned) == 0:
        return 0
    #print(avgIncome/len(incomesAssigned))
    return avgIncome/len(incomesAssigned)


#points are (x,y), rads are for radius A and B respectively
def isCircleIntersect(pointA, pointB, radA, radB):
    #print(pointA)
    #print(pointB)
    #print(radA)
    #print(radB)
    isIntersect = False
    c1c2 = ( ((pointA[0] - pointB[0])**2) + ((pointA[1] - pointB[1])**2))**0.5
    if (c1c2 == radA + radB):
        isIntersect = True
    elif(c1c2 > radA + radB):
        isIntersect = False
    else:
        isIntersect = True
    return isIntersect
def main():
    #medianIncomeDf = get_median_hh_income()
    #print(medianIncomeDf)
    fileName1 = "stops_with_incomeLevel.csv"
    fileName2 = "pati_bus_stops.csv"
    fileName4 = "bostonplansgroupeddata.csv"
    data1 = pd.read_csv(fileName1)
    #print(data1.head())
    data2 = pd.read_csv(fileName2)
    #print(data2.head())
    data3 = data1.merge(data2, left_on='STOP_ID', right_on='HastusId')
    data4 = pd.read_csv(fileName4)
    data4_np = data4.to_numpy()
    #print(data4_np)
    #assign stop income levels within radius of 0.5 of the stop to the stop
    #for each location with income level within the 0.5 radius assign it a median income
    #print(data3.head())
    #print(data3.loc(0)['STOP_ID'])
    #print(data3['STOP_ID'])
    stops = data3['STOP_ID']
    #medians = data3['Income']
    #latitudes = data3['Latitude', 'Longitude']
    #longitudes = data3['Longitude']
    #print(latitudes)
    #print(longitudes)
    geoLoc = data3[['STOP_ID','Latitude', 'Longitude', 'income']]
    #print(geoLoc)
    #radius = 0.5 #in miles
    #radius = radius * 1.609344 * 1000 #in meters
    #radius = radius * (1/1850) #in degrees
    radius = 0.5 * (1/68.703)
    print(radius)
    #print(radius)
    Xset = [] #the set of points of area to income level if we can find it
    #toList() or to_numpy()
    medianIncomeLs = []
    for index,row in geoLoc.iterrows():
        #print([row['STOP_ID']])
        point = (row['Latitude'], row['Longitude'])
        #print(point)
        tractIncome = row['income']
        mIncome = assignStopToMedianIncome(point, data4_np, radius)
        #print(mIncome)
        if (mIncome != 0):
            #If there is insufficient data from the bostonarea data4
            medianIncomeLs.append(mIncome)
            #print(mIncome)
        else:
            #just append the tractIncome.
            #print(mIncome)
            medianIncomeLs.append(tractIncome)

    print(medianIncomeLs)
    print(min(medianIncomeLs))
    mins = float('inf')
    minStopId = 0
    ind = 0
    for index, row in geoLoc.iterrows():
        if (medianIncomeLs[ind] < mins):
            mins = medianIncomeLs[ind]
            minStopId = int(row['STOP_ID'])
        ind += 1
    print(mins)
    print(minStopId)
main()
