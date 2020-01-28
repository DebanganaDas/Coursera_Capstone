#!/usr/bin/env python
# coding: utf-8

# In[9]:


import folium
import pandas as pd
import json # library to handle JSON files
import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe


# In[10]:


dff = pd.read_csv(r'C:\Users\debandas\Desktop\export.csv')


# In[11]:


# Map method of folium return Map object 
  
# Here we pass coordinates of Gfg  
# and starting Zoom level = 12 
my_map1 = folium.Map(location = [43.6532, -79.3832], 
                                        zoom_start = 12 ) 
  
# save method of Map object will create a map 
my_map1.save(" my_map1.html " ) 

# add markers to map
for lat, lng, borough, neighborhood in zip(dff['Latitude'], dff['Longitude'], dff['Borough'], dff['Neighbourhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(my_map1)  

my_map1.save(" my_map8.html " ) 
    


# In[12]:


CLIENT_ID = 'TROX1ND0M5PD2EDP04W0EN115KHNTGN5ZRKRSFBLTG12N31B' # your Foursquare ID
CLIENT_SECRET = 'CXXVLYWCJSRE0OCW2IBY5MCGY24CLAT0ALTHEGMRSUUKSY1B' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[18]:


LIMIT = 100 # limit of number of venues returned by Foursquare API



radius = 500 # define radius

url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
    CLIENT_ID, 
    CLIENT_SECRET, 
    VERSION, 
    43.7532586, 
    -79.3296565, 
    radius, 
    LIMIT)
url 
            
  


# In[19]:


results = requests.get(url).json()
results



# In[20]:


# function that extracts the category of the venue
def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


# In[21]:


venues = results['response']['groups'][0]['items']
    
nearby_venues = json_normalize(venues) # flatten JSON

# filter columns
filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng']
nearby_venues =nearby_venues.loc[:, filtered_columns]

# filter the category for each row
nearby_venues['venue.categories'] = nearby_venues.apply(get_category_type, axis=1)

# clean columns
nearby_venues.columns = [col.split(".")[-1] for col in nearby_venues.columns]

nearby_venues.head()


# In[22]:


print('{} venues were returned by Foursquare.'.format(nearby_venues.shape[0]))


# In[25]:


def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])
        nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[27]:



torontto_venues = getNearbyVenues(names=dff['Neighbourhood'],
                                   latitudes=dff['Latitude'],
                                   longitudes=dff['Longitude']
                                  )


# In[29]:


torontto_venues.groupby('Neighborhood').count()


# In[32]:


# one hot encoding
torontto_onehot = pd.get_dummies(torontto_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
torontto_onehot['Neighborhood'] = torontto_venues['Neighborhood'] 

# move neighborhood column to the first column
fixed_columns = [torontto_onehot.columns[-1]] + list(torontto_onehot.columns[:-1])
torontto_onehot = torontto_onehot[fixed_columns]

torontto_onehot.head()


# In[33]:


torontto_grouped = torontto_onehot.groupby('Neighborhood').mean().reset_index()
torontto_grouped


# In[34]:


def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# In[36]:


import numpy as np
num_top_venues = 10

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Neighborhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
neighborhoods_venues_sorted = pd.DataFrame(columns=columns)
neighborhoods_venues_sorted['Neighborhood'] = torontto_grouped['Neighborhood']

for ind in np.arange(torontto_grouped.shape[0]):
    neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(torontto_grouped.iloc[ind, :], num_top_venues)

neighborhoods_venues_sorted.head()


# In[43]:


from sklearn.cluster import KMeans


# In[44]:


# set number of clusters
kclusters = 5

torontto_grouped_clustering = torontto_grouped.drop('Neighborhood', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(torontto_grouped_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:10] 


# In[51]:


# add clustering labels
#neighborhoods_venues_sorted.insert(0, 'Cluster Labels', kmeans.labels_)

torontto_merged = dff

# merge toronto_grouped with toronto_data to add latitude/longitude for each neighborhood
torontto_merged = torontto_merged.join(neighborhoods_venues_sorted.set_index('Neighborhood'), on='Neighbourhood')

torontto_merged.head() # check the last columns!


# In[56]:


import matplotlib.cm as cm
import matplotlib.colors as colors

# create map
map_clusters = folium.Map(location=[43.6532, -79.3832], zoom_start=11)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(torontto_merged['Latitude'], torontto_merged['Longitude'], torontto_merged['Neighbourhood'], torontto_merged['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        #color=rainbow[cluster-1],
        fill=True,
        #fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters.save(" torontto.html " ) 


# In[55]:


torontto_merged.loc[torontto_merged['Cluster Labels'] == 0, torontto_merged.columns[[1] + list(range(5, torontto_merged.shape[1]))]]


# In[57]:


torontto_merged.loc[torontto_merged['Cluster Labels'] == 1, torontto_merged.columns[[1] + list(range(5, torontto_merged.shape[1]))]]


# In[58]:


torontto_merged.loc[torontto_merged['Cluster Labels'] == 2, torontto_merged.columns[[1] + list(range(5, torontto_merged.shape[1]))]]


# In[59]:


torontto_merged.loc[torontto_merged['Cluster Labels'] == 3, torontto_merged.columns[[1] + list(range(5, torontto_merged.shape[1]))]]


# In[60]:


torontto_merged.loc[torontto_merged['Cluster Labels'] == 4, torontto_merged.columns[[1] + list(range(5, torontto_merged.shape[1]))]]


# In[ ]:




