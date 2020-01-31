#!/usr/bin/env python
# coding: utf-8

# In[54]:


import pandas as pd
import numpy as np
df = pd.read_csv(r'C:\Users\debandas\Downloads\mumbai.csv')


# In[55]:


df.head()


# In[3]:


import folium
  
# Map method of folium return Map object 
  
# Here we pass coordinates of Gfg  
# and starting Zoom level = 12 
my_map1 = folium.Map(location = [19.0760, 72.8777], 
                                        zoom_start = 12 ) 
  
# save method of Map object will create a map 
my_map1.save(" mumbai.html " ) 

# add markers to map
for lat, lng, price, neighborhood in zip(df['Latitude'], df['Longitude'], df['Average price/sqft'], df['Neighbourhood']):
    label = '{}, {}'.format(neighborhood, price)
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

my_map1.save(" mumbai.html " ) 


# In[56]:


CLIENT_ID = 'TROX1ND0M5PD2EDP04W0EN115KHNTGN5ZRKRSFBLTG12N31B' # your Foursquare ID
CLIENT_SECRET = 'CXXVLYWCJSRE0OCW2IBY5MCGY24CLAT0ALTHEGMRSUUKSY1B' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[57]:


LIMIT = 100 # limit of number of venues returned by Foursquare API



radius = 500 # define radius

url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
    CLIENT_ID, 
    CLIENT_SECRET, 
    VERSION, 
    19.0760, 
    72.8777, 
    radius, 
    LIMIT)
url 
            


# In[58]:


import json # library to handle JSON files
import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe
results = requests.get(url).json()
results


# In[59]:


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


# In[60]:


venues = results['response']['groups'][0]['items']
    
nearby_venues = json_normalize(venues) # flatten JSON

# filter columns
filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng']
nearby_venues =nearby_venues.loc[:, filtered_columns]

# filter the category for each row
nearby_venues['venue.categories'] = nearby_venues.apply(get_category_type, axis=1)

# clean columns
nearby_venues.columns = [col.split(".")[-1] for col in nearby_venues.columns]

nearby_venues.head(50)


# In[61]:


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


# In[62]:


mumbai_venues = getNearbyVenues(names=df['Neighbourhood'],
                                   latitudes=df['Latitude'],
                                   longitudes=df['Longitude']
                                  )


# In[63]:


mumbai_venues.groupby('Neighborhood').count()


# In[64]:


# one hot encoding
mumbai_onehot = pd.get_dummies(mumbai_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
mumbai_onehot['Neighborhood'] = mumbai_venues['Neighborhood'] 

# move neighborhood column to the first column
fixed_columns = [mumbai_onehot.columns[-1]] + list(mumbai_onehot.columns[:-1])
mumbai_onehot = mumbai_onehot[fixed_columns]

mumbai_onehot.head()


# In[65]:


mumbai_grouped = mumbai_onehot.groupby('Neighborhood').mean().reset_index()
mumbai_grouped


# In[66]:


def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# In[67]:


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
neighborhoods_venues_sorted['Neighborhood'] = mumbai_grouped['Neighborhood']

for ind in np.arange(mumbai_grouped.shape[0]):
    neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(mumbai_grouped.iloc[ind, :], num_top_venues)

neighborhoods_venues_sorted.head()
df2 = pd.read_csv(r'C:\Users\debandas\Downloads\mumbaibins.csv')
dff = pd.merge(neighborhoods_venues_sorted, df2, on='Neighborhood')
dff.head(50)
Housing = dff.to_csv (r'C:\Users\debandas\Desktop\HousingBin.csv', index = None, header=True) #Don't forget to add '.csv' at the end of the path


# In[68]:


mumbai_grouped.head()


# In[69]:


from sklearn.cluster import KMeans 
from sklearn import metrics 
from scipy.spatial.distance import cdist


# In[70]:


import matplotlib.pyplot as plt  
mumbai_grouped_clustering = mumbai_grouped.drop('Neighborhood', 1)


# In[23]:


distortions = [] 
inertias = [] 
mapping1 = {} 
mapping2 = {} 
K = range(1,10) 

for k in K: 
	#Building and fitting the model 
	kmeanModel = KMeans(n_clusters=k).fit(mumbai_grouped_clustering) 
	kmeanModel.fit(mumbai_grouped_clustering)	 
	
	distortions.append(sum(np.min(cdist(mumbai_grouped_clustering, kmeanModel.cluster_centers_, 
					'euclidean'),axis=1)) / mumbai_grouped_clustering.shape[0]) 
	inertias.append(kmeanModel.inertia_) 

	mapping1[k] = sum(np.min(cdist(mumbai_grouped_clustering, kmeanModel.cluster_centers_, 
				'euclidean'),axis=1)) / mumbai_grouped_clustering.shape[0] 
	mapping2[k] = kmeanModel.inertia_ 

for key,val in mapping1.items(): 
	print(str(key)+' : '+str(val)) 

plt.plot(K, distortions, 'bx-') 
plt.xlabel('Values of K') 
plt.ylabel('Distortion') 
plt.title('The Elbow Method using Distortion') 
plt.show() 


# In[24]:


plt.plot(K, inertias, 'bx-') 
plt.xlabel('Values of K') 
plt.ylabel('Inertia') 
plt.title('The Elbow Method using Inertia') 
plt.show() 


# ### run k-means clustering
# kclusters = 3
# kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(mumbai_grouped_clustering)
# 
# # check cluster labels generated for each row in the dataframe
# kmeans.labels_[0:0] 

# 

# ##### set number of clusters
# kclusters = 
# 
# mumbai_grouped_clustering = mumbai_grouped.drop('Neighborhood', 1)
# 
# # run k-means clustering
# kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(mumbai_grouped_clustering)
# 
# # check cluster labels generated for each row in the dataframe
# kmeans.labels_[0:10] 

# ###### set number of clusters
# kclusters = 
# 
# mumbai_grouped_clustering = mumbai_grouped.drop('Neighborhood', 1)
# 
# # run k-means clustering
# kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(mumbai_grouped_clustering)
# 
# # check cluster labels generated for each row in the dataframe
# kmeans.labels_[0:10] 

# In[71]:


# set number of clusters
kclusters = 7

mumbai_grouped_clustering = mumbai_grouped.drop('Neighborhood', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(mumbai_grouped_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:10] 


# In[73]:


# add clustering labels
#neighborhoods_venues_sorted.drop(df.columns[0],axis=1)
#del neighborhoods_venues_sorted['Cluster Labels']
#neighborhoods_venues_sorted.drop(columns=['Cluster Labels'])
#neighborhoods_venues_sorted.head()
neighborhoods_venues_sorted.insert(0, 'Cluster Labels', kmeans.labels_)

mumbai_merged = df

# merge toronto_grouped with toronto_data to add latitude/longitude for each neighborhood
mumbai_merged = mumbai_merged.join(neighborhoods_venues_sorted.set_index('Neighborhood'), on='Neighbourhood')

mumbai_merged.head(50) # check the last columns!


# In[74]:


mumbai_merged.head(50)
data = mumbai_merged.to_csv (r'C:\Users\debandas\Desktop\data.csv', index = None, header=True) #Don't forget to add '.csv' at the end of the path


# In[75]:


import matplotlib.cm as cm
import matplotlib.colors as colors

# create map
map_clusters = folium.Map(location=[19.0760, 72.8777], zoom_start=11)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(mumbai_merged['Latitude'], mumbai_merged['Longitude'], mumbai_merged['Neighbourhood'], mumbai_merged['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters.save(" mumbaicluster.html " ) 


# In[76]:


mumbai_merged.loc[mumbai_merged['Cluster Labels'] == 1, mumbai_merged.columns[[1] + list(range(5, mumbai_merged.shape[1]))]]


# In[77]:


mumbai_merged.loc[mumbai_merged['Cluster Labels'] == 6, mumbai_merged.columns[[1] + list(range(5, mumbai_merged.shape[1]))]]


# In[78]:


mumbai_merged.loc[mumbai_merged['Cluster Labels'] == 0, mumbai_merged.columns[[1] + list(range(5, mumbai_merged.shape[1]))]]


# In[79]:


mumbai_merged.loc[mumbai_merged['Cluster Labels'] == 3, mumbai_merged.columns[[1] + list(range(5, mumbai_merged.shape[1]))]]


# In[82]:


mumbai_merged.head()


# In[87]:


mumbai_merged.head()
df3 = pd.read_csv(r'C:\Users\debandas\Downloads\mumbaicluster.csv')
df4 = pd.merge(mumbai_merged, df3, on='Neighbourhood')
df4.head()
HousingCluster = df4.to_csv(r'C:\Users\debandas\Desktop\HousingCluster.csv', index = None, header=True) #Don't forget to add '.csv' at the end of the path


# In[ ]:




