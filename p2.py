# -*- coding: utf-8 -*-
"""p2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hnvtR_RNz3jVVfpvUVCEhaLLsKFGZ2Y6
"""

# Loading required libraries
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.cluster import k_means
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

"""# Reading Dataset"""

pd.set_option('display.max_columns', None)
world=pd.read_excel("World_development_mesurement.xlsx")
world.head()

"""# Exploratory Data Analysis"""

# information about dataset
info = pd.DataFrame(world.info())

# Sum of null values in each feature
world.isnull().sum()

# Renaming columns
world.rename(columns={'Birth Rate':'birth_rate', 'Business Tax Rate':'business_tax_rate','CO2 Emissions':'co2_emission','Country':'country',
                      'Days to Start Business':'days_to_start_business','Ease of Business':'ease_of_business','Energy Usage':'energy_usage',
                      'Gdp':'gdp','Health Exp % GDP':'health_exp_percent_GDP','Health Exp/Capita' :'health_exp_percapita',
                      'Hours to do Tax':'hours_to_do_tax','Infant Mortality Rate':'infant_mortality_rate','Internet Usage':'internet_usage',
                      'Lending Interest':'lending_interest','Life Expectancy Female':'life_expectancy_female','Life Expectancy Male':'life_expectancy_male',
                      'Mobile Phone Usage':'mobile_phone_usage','Number of Records':'no_of_records','Population 0-14':'population_0_14',
                      'Population 15-64':'population_15_64', 'Population 65+':'population_65_plus','Population Total':'population_total','Population Urban':'population_urban',
                      'Tourism Inbound':'tourism_inbound','Tourism Outbound':'tourism_outbound'}, inplace=True)

world.head()

# Dropping columns "Ease of Business & No. of Records"
'''here we are deleting Ease of business because there are 2519 null values out of 2704 rows ,
 and we also delete  Number of Records having only 1 as a value '''

world_2 = world.drop(columns=['ease_of_business','no_of_records'] , axis=1)

# Removing Special Characters ($, %)
''' Here we are replacing  "$", "%" and "," symbol with space'''

colstocheck = world_2.columns
world_2[colstocheck] = world_2[colstocheck].replace({'\$|\%|\,':""}, regex = True)

world_2.head()

# Calculating percentage of missing/null values
percent_missing = round(world_2.isnull().sum() * 100 / len(world_2),3)
percent_missing.sort_values(ascending=False)

# Heatmap for null values
plt.figure(figsize=(16,8))
sns.heatmap(world_2.isnull())
plt.show()

# Converting Object datatypes to Numeric Datatypes
world_2["GDP"] = pd.to_numeric(world_2["GDP"], errors='coerce')
world_2["tourism_inbound"] = pd.to_numeric(world_2["tourism_inbound"], errors='coerce')
world_2["tourism_outbound"] = pd.to_numeric(world_2["tourism_outbound"], errors='coerce')
world_2['business_tax_rate'] = pd.to_numeric(world_2['business_tax_rate'], errors='coerce')
world_2['health_exp_percapita'] = pd.to_numeric(world_2['health_exp_percapita'], errors='coerce')

# Checking dataset info after converting the datatypes
world_2.info()

# Describing the data
world_2.describe().T

"""## Interpretations on Data Description

* co2_emission, energy_usage, GDP, health_exp_percapita, population_total, tourism_inbound, tourism_outbound mean values are far away from the 50% of the data.

* Remaining features are somewhat nearby the 50% of data.
"""

features = world_2.drop(columns='country',axis = 1)

features.skew().sort_values(ascending=False)

for i in features:

    world_2[i].hist(bins=25)
    plt.ylabel('Count')
    plt.title(i)
    plt.show()

"""## Interpretations on Skewness of Features

* lending_interest, GDP, population_total, co2_emission, days_to_start_business, tourism_inbound, energy_usage, tourism_outbound features are highly skewed

* Need to find a way to reduce the skewness for the above mentioned features

# Before imputation let us check for outliers using boxplot and histograms
"""

for i in features:
    plt.figure(figsize=(12,2))
    plt.boxplot(world_2[i].dropna(),vert=False,)
    plt.title(i)
    plt.show()

"""## Interpretations on Boxplots
* business_tax_rate, co2_emission, days_to_start_business, energy_usage, GDP, health_exp%_GDP, health_exp_percapita, hours_to_do tax, population_total, tourism_inbound, tourism_outbound are having more number of Outliers

* infant_mortality_rate, life_expectancy_female, life_expectancy_male, moble_phone_usage, population_15_64, population_65+ are having few number of Outliers

* The boxplots of Birth Rate,Ease of Business ,Mobile Phone Usage,Internet Usage,Infant Mortality Rate,Life Expectancy Female,Life Expectancy Male,,Population 0-14,Population 15-64,Population 65+, Population Urban looks fine.

*  few outliers are detected but it make sense as it is global data and not much deviated from the actual values.

*  max(Business Tax Rate) is around 340% , which means paying 340 rupees as tax for every 100 rupees profit. The global highest Business Tax Rate is around 55% , so assuming the max value to be 60% and replacing all the ouliers (i.e., above 60%) with np.nan and will fill them later using imputation techniques

*  max(Days to Start Business) is 694 days. Accounting 18-20 business days a month it takes like around 3 years , comparing it to real time global values the max time required to start a business is around 50 days.Based on the boxplot assuming the max days to start a business is 80 days and replacing all the outliers with np.nan and will figure a way to fill them up with sensible number later based on all other parameters

*  Based on the boxplot assuming 600 hours as max(hours to do tax ) and replacing all the outliers with np.nan and will figure a way to fill them up with sensible number later based on all other parameters.
"""

world_2['business_tax_rate'] =np.where(world_2['business_tax_rate']>60 ,np.nan,world_2['business_tax_rate'])
world_2['days_to_start_business'] =np.where(world_2['days_to_start_business']>80 ,np.nan,world_2['days_to_start_business'])
world_2['hours_to_do_tax'] =np.where(world_2['hours_to_do_tax']>600 ,np.nan,world_2['hours_to_do_tax'])

"""###  Note:  Removing outliers of the business_tax_rate, days_to_start_business, hours_to_do_tax. there is no sense as the feature values are practically taken from the real world and depends on the population and gdp of the countries which varey significantly from one another

"""

# Calculating percentage of missing/null values
percent_missing =  world_2.isnull().sum() * 100 / len(world_2)
percent_missing.sort_values(ascending=False)

"""## Interpretations on Missing Values
* Most of the features are having missing values.

* hours_to_do tax, business_tax_rate, days_to_start_business, energy_usage, lending_interest are the top 5 features with highest percentage of missing values.
"""

# Describing the data
world_2.describe().T

"""# Country & Feature wise Mean Imputation
* Imputing missing values with country and feature wise mean, as if the imputation is done through the mean of feature may mislead the data.
"""

for i in world_2.columns:
    null_df = world_2[world_2[i].isnull()]
    print(i, " is having missing values from ", null_df['country'].nunique(), " countries.")
    print("--------------------------------------------------------------------------------")

world_fill_mean_na = world_2.copy()

mean_fill_cols = world_fill_mean_na.drop(columns=['country', 'population_total']).columns

final_df_after_mean_imputation = pd.DataFrame()
for col in mean_fill_cols:
    fill_na_df = world_fill_mean_na[['country', col]]
    fill_na_df[col] = fill_na_df.groupby("country")[col].transform(lambda x: x.fillna(x.mean()))
    final_df_after_mean_imputation = pd.concat([final_df_after_mean_imputation, fill_na_df], axis=1)

final_df_after_mean_imputation.shape

final_df_after_mean_imputation = final_df_after_mean_imputation.drop(columns=['country'])

final_df_after_mean_imputation.shape

final_df_after_mean_imputation['country'] = world_fill_mean_na['country']
final_df_after_mean_imputation['population_total'] = world_fill_mean_na['population_total']

final_df_after_mean_imputation.head()

# Example of Country which is having null values for the entire feature
example_df = final_df_after_mean_imputation[['country', 'energy_usage']]
example_df[example_df['country'] == 'Afghanistan']

# Calculating percentage of missing/null values after imputing with country and feature wise mean
percent_missing =  final_df_after_mean_imputation.isnull().sum() * 100 / len(world_2)
percent_missing.sort_values(ascending=False)

final_df_after_mean_imputation.describe().T

"""# Median Imputation"""

median_data = final_df_after_mean_imputation.drop(columns = ["country"],axis=1)
median_data.fillna(median_data.median(), inplace=True)

"""### Whichever countries having null values for the entire feature, imputing those countries with median value of that feature from all the countries."""

median_data.describe().T

median_data['country'] = final_df_after_mean_imputation['country']

median_data.head()

median_data.isnull().sum()

"""# KNN Imputation"""

# # KNN Imputation
# from sklearn.impute import KNNImputer
# imputer = KNNImputer(n_neighbors=25)
# knn_data = final_df_after_mean_imputation.drop(columns = ["country"],axis=1)
# knn_imputed_data = imputer.fit_transform(knn_data)

# cols = knn_data.columns
# knn_imputed_df = pd.DataFrame(knn_imputed_data, columns=cols)

# knn_imputed_df.isnull().sum()

# knn_imputed_df['country'] = final_df_after_mean_imputation['country']

# data_after_imputation = knn_imputed_df[['birth_rate', 'business_tax_rate', 'co2_emission', 'country',
#        'days_to_start_business', 'energy_usage', 'GDP', 'health_exp%_GDP',
#        'health_exp_percapita', 'hours_to_do tax', 'infant_mortality_rate',
#        'internet_usage', 'lending_interest', 'life_expectancy_female',
#        'life_expectancy_male', 'moble_phone_usage', 'population_0_14',
#        'population_15_64', 'population_65+', 'population_total',
#        'population_urban', 'tourism_inbound', 'tourism_outbound']]

"""### Tried with KNN Imputation as well for whichever countries having null values for the entire feature, but median imputation is giving better results, hence going ahead with median imputation"""

data_after_imputation = median_data[['birth_rate', 'business_tax_rate', 'co2_emission', 'country',
       'days_to_start_business', 'energy_usage', 'GDP', 'health_exp_percent_GDP',
       'health_exp_percapita', 'hours_to_do_tax', 'infant_mortality_rate',
       'internet_usage', 'lending_interest', 'life_expectancy_female',
       'life_expectancy_male', 'mobile_phone_usage', 'population_0_14',
       'population_15_64', 'population_65_plus', 'population_total',
       'population_urban', 'tourism_inbound', 'tourism_outbound']]

"""### Data Sanity Check"""

pd.set_option('display.max_columns', None)
world_2.head()

data_after_imputation.head()

data_after_imputation.describe().T

data_after_imputation.duplicated().sum()

world_development_final_data =  data_after_imputation.copy()

world_development_final_data.skew().sort_values(ascending=False)

"""# Boxplots after Imputation"""

features = world_development_final_data.drop(columns="country",axis=1)
for i in features:
    plt.figure(figsize=(12,2))
    plt.boxplot(world_development_final_data[i].dropna(),vert=False,)
    plt.title(i)
    plt.show()

"""# Data Transformations"""

# Data Transformtions
world_development_final_data['lending_interest'] = np.log(world_development_final_data['lending_interest'])
world_development_final_data[['GDP', 'co2_emission', 'population_total', 'energy_usage', 'tourism_inbound', 'tourism_outbound']] = np.sqrt(world_development_final_data[['GDP', 'co2_emission', 'population_total', 'energy_usage', 'tourism_inbound', 'tourism_outbound']])

"""* Applying log transformation for lending_interest feature
* Applying Square root transformation for 'GDP', 'co2_emission', 'population_total', 'energy_usage', 'tourism_inbound', 'tourism_outbound' features
"""

world_development_final_data.skew().sort_values(ascending=False)

# Correaltion matrix
world_development_final_data.corr()

# Heatmap for Correlation
plt.figure(figsize =(16,10))
sns.heatmap(world_development_final_data.corr(),annot =True)
plt.show()

"""# Boxplots After Data Transformation"""

features_1 = world_development_final_data.drop(columns="country",axis=1)
# Histograms for numerical features
for i in features_1:
    world_development_final_data[i].hist(bins=25)
    plt.ylabel('Count')
    plt.title(i)
    plt.show()

#Top 30 countries with highest and lowest GDP

df_gdp_country = world_development_final_data.groupby('country', group_keys=False).apply(lambda x: x.loc[x.GDP.idxmax()])

# df_gdp_country
top40 = df_gdp_country['GDP'].sort_values(ascending=False)[:30]
bot40 = df_gdp_country['GDP'].sort_values()[:30]

plt.figure(figsize=(20,8), dpi=80)
top = sns.barplot(x=top40, y=top40.index, log=True)
plt.title('Top 30 countries with Highest GDP')
plt.show()

plt.figure(figsize=(20,8), dpi=80)
bot = sns.barplot(x=bot40, y=bot40.index, log=True)
plt.title('Top 30 countries with Lowest GDP')
plt.show()

#Top 30 countries highest and lowest Tourism Inbound

df_ti_country = world_development_final_data.groupby('country', group_keys=False).apply(lambda x: x.loc[x['tourism_inbound'].idxmax()])

# df_gdp_country
top30 = df_ti_country['tourism_inbound'].sort_values(ascending=False)[:30]
bot30 = df_ti_country['tourism_inbound'].sort_values()[:30]

plt.figure(figsize=(20,8), dpi=80)
sns.barplot(x=top30, y=top30.index, log=True)
plt.title('Top 30 countries with Highest Tourism Inbound')
plt.show()

plt.figure(figsize=(20,8), dpi=80)
sns.barplot(x=bot30, y=bot30.index, log=True)
plt.title('Top 30 countries with lowest Tourism Inbound')
plt.show()

#Top 30 countries highest and lowest Tourism Outbound¶

df_to_country = world_development_final_data.groupby('country', group_keys=False).apply(lambda x: x.loc[x['tourism_outbound'].idxmax()])

# df_gdp_country
top30 = df_to_country['tourism_outbound'].sort_values(ascending=False)[:30]
bot30 = df_to_country['tourism_outbound'].sort_values()[:30]

plt.figure(figsize=(20,8), dpi=80)
top_bp = sns.barplot(x=top30, y=top30.index, log=True)
plt.title("Top 30 countries with highest Tourism Outbound")
plt.show()

plt.figure(figsize=(20,8), dpi=80)
bot_bp = sns.barplot(x=bot30, y=bot30.index, log=True)
plt.title("Top 30 countries witth lowest Tourism Outbound")
plt.show()

#Top 30 countries highest and lowest Energy Usage

df_eu_country = world_development_final_data.groupby('country', group_keys=False).apply(lambda x: x.loc[x['energy_usage'].idxmax()])

# df_gdp_country
top30 = df_eu_country['energy_usage'].sort_values(ascending=False)[:30]
bot30 = df_eu_country['energy_usage'].sort_values()[:30]

plt.figure(figsize=(20,8), dpi=80)
top_bp = sns.barplot(x=top30, y=top30.index, log=True)
plt.title("Top 30 countries highest Energy Usage")
plt.show()

plt.figure(figsize=(20,8), dpi=80)
bot_bp = sns.barplot(x=bot30, y=bot30.index, log=True)
plt.title("Top 30 countries lowest Energy Usage")
plt.show()

#Top 30 countries highest and lowest CO2 Emissions

df_ce_country = world_development_final_data.groupby('country', group_keys=False).apply(lambda x: x.loc[x['co2_emission'].idxmax()])

# df_gdp_country
top30 = df_ce_country['co2_emission'].sort_values(ascending=False)[:30]
bot30 = df_ce_country['co2_emission'].sort_values()[:30]

plt.figure(figsize=(20,8), dpi=80)
top_bp = sns.barplot(x=top30, y=top30.index, log=True)
plt.title("Top 30 countries highest CO2 Emission")
plt.show()

plt.figure(figsize=(20,8), dpi=80)
bot_bp = sns.barplot(x=bot30, y=bot30.index, log=True)
plt.title("Top 30 countries lowest CO2 Emission")
plt.show()

"""## Hopkins test
* Hopkins test  is a way of measuring the cluster tendency of a dataset the Hopkins statistic, is a statistic which gives a value which indicates the cluster tendency, in other words: how well the data can be clustered.
* If the value is between {0.01, ...,0.3}, the data is regularly spaced.
* If the value is around 0.5, it is random.
* If the value is between {0.7, ..., 0.99}, it has a high tendency to cluster.measuring
"""

#Calculating the Hopkins statistic
from sklearn.neighbors import NearestNeighbors
from random import sample
from numpy.random import uniform
import numpy as np
from math import isnan

#Function to calculate Hopkins test score
def hopkins(X):
    d = X.shape[1]
    n = len(X) # rows
    m = int(0.1 * n)
    nbrs = NearestNeighbors(n_neighbors=1).fit(X.values)

    rand_X = sample(range(0, n, 1), m)

    ujd = []
    wjd = []
    for j in range(0, m):
        u_dist, _ = nbrs.kneighbors(uniform(np.amin(X,axis=0),np.amax(X,axis=0),d).reshape(1, -1), 2, return_distance=True)
        ujd.append(u_dist[0][1])
        w_dist, _ = nbrs.kneighbors(X.iloc[rand_X[j]].values.reshape(1, -1), 2, return_distance=True)
        wjd.append(w_dist[0][1])

    H = sum(ujd) / (sum(ujd) + sum(wjd))
    if isnan(H):
        print(ujd, wjd)
        H = 0

    return H

features_1.columns

hopkins(features_1)

"""Hopkins test results will vary as it picks a set of samples each time. On running it multiple times, it can be seen that this data set gives Hopkins statistic value in the range of 0.88 to 0.97 and hence our dataset is good for clustering and lets proceed our analysis

# Standardization
"""

# Scaling on numerical features
scaler = MinMaxScaler() # instantiate scaler
scaled_info = scaler.fit_transform(features_1)# fit and transform numerical data of given dataset
scaled_df = pd.DataFrame(scaled_info, columns = features_1.columns) # convert to dataframe
scaled_df.head()

# # Scaling on numerical features
# scaler = StandardScaler() # instantiate scaler
# scaled_info = scaler.fit_transform(features)# fit and transform numerical data of given dataset
# scaled_df = pd.DataFrame(scaled_info, columns = features.columns) # convert to dataframe
# scaled_df.head()

"""# Agglomeritive or Hierarchical Clustering"""

# create dendrogram
world_development1=world_development_final_data.copy()
import scipy.cluster.hierarchy as sch
plt.figure(figsize=(20, 15))
dendograms=sch.dendrogram(sch.linkage(scaled_info,"complete"))

model=AgglomerativeClustering(n_clusters=3,affinity="euclidean",linkage="complete")
cluster_numbers=model.fit_predict(scaled_info)

world_development1['Hierarchical_Cluster_tag']=cluster_numbers

world_development1.Hierarchical_Cluster_tag.unique()

world_development1['Hierarchical_Cluster_tag'].value_counts()

# silhouette score
sil_score= silhouette_score(scaled_info, model.labels_)
print('silhouette score: ',sil_score)

"""# K-Means Clustering"""

world_development1 = world_development1.drop(columns=['Hierarchical_Cluster_tag'], axis=1)

from sklearn.cluster import KMeans
WCSS = []
for i in range(1,10):
    k = KMeans(n_clusters=i).fit(scaled_info)
    WCSS.append(k.inertia_)
plt.plot(range(1,10),WCSS)
plt.title('Elbow Method')
plt.xlabel('no.of clusters')
plt.ylabel('WCSS')
plt.show()

!pip install Kneed

## Getting Optimal K value
from kneed import KneeLocator

y = WCSS
x = range(1, len(y)+1)

kn = KneeLocator(x, y, curve= 'convex', direction='decreasing')
print("Optimal Number of Clusters is ", kn.knee)

plt.plot(x, y, 'bx--')
plt.xlabel('Number of Clusters')
plt.ylabel('Distances')
plt.vlines(kn.knee, plt.ylim()[1], plt.xlim()[1], linestyles='dotted')
plt.show()

"""#### From the above elbow method diagram we can say that no.of clusters = 3."""

model1=KMeans(n_clusters=3, random_state=5, init='k-means++', n_init=15,
               max_iter=500,)
cluster_numbers=model1.fit_predict(scaled_info)

world_development1['Kmeans_Cluster_tag']=cluster_numbers

world_development1['Kmeans_Cluster_tag'].value_counts()

import matplotlib.pyplot as plt

world_development1['Kmeans_Cluster_tag'].value_counts().plot(kind='bar',figsize = (8,6))
plt.xlabel("clusters",loc="center",fontsize= 20,fontweight= "bold")
plt.ylabel("ID Counts",loc="center",fontsize=20,fontweight= "bold")
plt.yticks(fontsize=15)
plt.xticks(fontsize=15)
plt.show()

# silhouette score
sil_score_kmeans= silhouette_score(scaled_info, model1.labels_)
print('silhouette score: ',sil_score_kmeans)

world_development1.groupby('Kmeans_Cluster_tag').mean().round(1).reset_index()

"""# Principal Component Analysis"""

from sklearn.decomposition import PCA
pca = PCA()
pca_values = pca.fit_transform(scaled_df)
variance = pca.explained_variance_ratio_ # it gives importance of each and every PCA
variance

var_cumulative = np.cumsum(np.round(variance, decimals= 3)*100)
var_cumulative

plt.figure(figsize=(10,4))
plt.scatter(x=[i+1 for i in range(len(pca.explained_variance_ratio_))],
            y=pca.explained_variance_ratio_,
           s=200, alpha=0.75,c='blue',edgecolor='k')
plt.grid(True)
plt.title("Explained variance ratio of the \nfitted principal component vector\n",fontsize=25)
plt.xlabel("Principal components",fontsize=10)
plt.xticks([i+1 for i in range(len(pca.explained_variance_ratio_))],fontsize=15)
plt.yticks(fontsize=10)
plt.ylabel("Explained variance ratio",fontsize=10)
plt.show()

# PCA for 3 components
pca = PCA(n_components=3)
pca_values = pca.fit_transform(scaled_df)
variance = pca.explained_variance_ratio_
variance

var_cumulative = np.cumsum(np.round(variance, decimals= 3)*100)
var_cumulative

## Creating Dataframe for top 7 PCA values
# pca_df = pd.DataFrame(pca_values ,columns=["PCA1","PCA2","PCA3", "PCA4", "PCA5", "PCA6", "PCA7", "PCA8", "PCA9"])
pca_df = pd.DataFrame(pca_values ,columns=["PCA1","PCA2","PCA3"])
pca_df.head(10)

import plotly.express as px
plt.figure(figsize=(30, 25))
fig = px.scatter_matrix(pca_values,
    labels={
    str(i): f"PC {i+1} ({var:.1f}%)"
    for i, var in enumerate(variance * 100)
},
    dimensions=range(3),
    color=world_development1['country']
)
fig.update_traces(diagonal_visible=False,)
fig.show()

"""# Agglomeritive or Hierarchical Clustering using PCA values"""

# create dendrogram
world_development2=world_development_final_data.copy()
import scipy.cluster.hierarchy as sch
plt.figure(figsize=(20, 15))
dendograms=sch.dendrogram(sch.linkage(pca_values,"complete"))

model=AgglomerativeClustering(n_clusters=3,affinity="euclidean",linkage="complete")
cluster_numbers=model.fit_predict(pca_values)

world_development2['Hierarchical_Cluster_tag']=cluster_numbers

world_development2.Hierarchical_Cluster_tag.unique()

world_development2['Hierarchical_Cluster_tag'].value_counts()

# silhouette score
sil_score= silhouette_score(pca_values, model.labels_)
print('silhouette score: ',sil_score)

"""# K-means clustering using PCA values"""

world_development2 = world_development2.drop(columns=['Hierarchical_Cluster_tag'], axis=1)

from sklearn.cluster import KMeans
WCSS = []
for i in range(1,10):
    k = KMeans(n_clusters=i, init='k-means++',
               n_init=15,
               max_iter=500,
               random_state=5).fit(pca_values)
    WCSS.append(k.inertia_)
plt.plot(range(1,10),WCSS)
plt.title('Elbow Method')
plt.xlabel('no.of clusters')
plt.ylabel('WCSS')
plt.show()

# We will also use the Silhouette score to determine an optimal number.

k = [2,3,4,5,6,7,8,9]

#  Silhouette score for MinMaxScaler Applied on data .

for n_clusters in k:
    clusterer1 = KMeans(n_clusters=n_clusters, random_state=0)
    cluster_labels1 = clusterer1.fit_predict(pca_values)
    sil_score1= silhouette_score(pca_values, cluster_labels1)
    print("For n_clusters =", n_clusters,"The average silhouette_score is :", sil_score1)

## Getting Optimal K value
from kneed import KneeLocator

y = WCSS
x = range(1, len(y)+1)

kn = KneeLocator(x, y, curve= 'convex', direction='decreasing')
print("No. of Optimal Clusters is ", kn.knee)

plt.plot(x, y, 'bx--')
plt.xlabel('Number of Clusters')
plt.ylabel('Distances')
plt.vlines(kn.knee, plt.ylim()[1], plt.xlim()[1], linestyles='dotted')
plt.show()

kmeans_model=KMeans(n_clusters=3, init='k-means++',
               n_init=15,
               max_iter=500,
               random_state=5)
cluster_numbers = kmeans_model.fit_predict(pca_values)

data_after_imputation['Cluster']=cluster_numbers

data_after_imputation['Cluster'].value_counts()

import matplotlib.pyplot as plt

data_after_imputation['Cluster'].value_counts().plot(kind='bar',figsize = (8,6))
plt.xlabel("clusters",loc="center",fontsize= 20,fontweight= "bold")
plt.ylabel("ID Counts",loc="center",fontsize=20,fontweight= "bold")
plt.yticks(fontsize=15)
plt.xticks(fontsize=15)
plt.show()

# silhouette score
sil_score_kmeans= silhouette_score(pca_values, kmeans_model.labels_)
print('silhouette score: ',sil_score_kmeans)

data_after_imputation.groupby('Cluster').mean().round(1).reset_index()

cluster_df =data_after_imputation.copy()
cluster_df

cluster_1_df = cluster_df[cluster_df["Cluster"]==0]
cluster_1_df

cluster_2_df = cluster_df[cluster_df["Cluster"]==1]
cluster_2_df

cluster_3_df = cluster_df[cluster_df["Cluster"]==2]
cluster_3_df

#Visualization
sns.countplot(x='Cluster', data=cluster_df)

for c in cluster_df.drop(['Cluster'],axis=1):
    grid= sns.FacetGrid(cluster_df, col='Cluster')
    grid= grid.map(plt.hist, c)
plt.show()

"""# Saving the kmeans clustering model and the data with cluster label"""

#Saving Scikitlearn models
import joblib
joblib.dump(kmeans_model, "kmeans_model.pkl")

cluster_df.to_csv("Clustered_ World_Development_Data.csv")

"""# Training and Testing the model accuracy using Random Forest

"""

#Split Dataset
X = cluster_df.drop(['Cluster','country'],axis=1)
# X =X[~X.isin([np.nan, np.inf, -np.inf]).any(1)]
# X.replace([np.inf, -np.inf], np.nan, inplace=True)
# new_X = X[np.isfinite(X).all(1)]
y= cluster_df['Cluster']
X_train, X_test, y_train, y_test =train_test_split(X, y, test_size=0.3, random_state=5)

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import StandardScaler

from sklearn import svm
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report


from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score

clf = SVC()
param_grid = [{'kernel':['rbf'],'gamma':[50,5,10,0.5],'C':[15,14,13,12,11,10,0.1,0.001] }]
gsv = GridSearchCV(clf,param_grid,cv=10)
gsv.fit(X_train,y_train)

clf=SVC()
clf.fit(X_train , y_train)
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred) * 100
print("Accuracy =", acc)
confusion_matrix(y_test, y_pred)

clf1 = SVC(kernel= "poly")
clf1.fit(X_train , y_train)
y_pred = clf1.predict(X_test)
acc = accuracy_score(y_test, y_pred) * 100
print("Accuracy =", acc)
confusion_matrix(y_test, y_pred)

gsv.best_params_ , gsv.best_score_

clf2 = SVC(C= 15, gamma = 50)
clf2.fit(X_train , y_train)
y_pred = clf2.predict(X_test)
acc = accuracy_score(y_test, y_pred) * 100
print("Accuracy =", acc)
confusion_matrix(y_test, y_pred)

#Confusion_Matrix
from sklearn.metrics import classification_report,confusion_matrix
import sklearn.metrics as metrics
print("Confusion Matrix")
print("____________________")
print(metrics.confusion_matrix(y_test, y_pred))
print("####################################################")
print("Classification Report")
print("______________________")
print(classification_report(y_test, y_pred))

print(X_train.shape)
print(y_train.shape)
print(X_test.shape)
print(y_test.shape)

import pickle
from pickle import dump,load
filename = 'world_model.pkl'
pickle.dump(clf, open(filename, 'wb'))# it wiil create a final model.sav file

# some time later...

# load the model from disk
loaded_model = pickle.load(open(filename, 'rb')) # this line will load data to final model.sav
result = loaded_model.score(X_test, y_test)
print(result,'% Acuuracy')

# installing streamlit library
! pip install streamlit

from PIL import Image
import pandas as pd
# loading the saved model
loaded_model = pickle.load(open(r'world_model.pkl','rb'))
df=pd.read_excel("World_development_mesurement.xlsx")

def Cluster_prediction(input_data):


    # changing the input_data to numpy array
    input_data_as_numpy_array = np.asarray(input_data)

    # reshape the array as we are predicting for one instance
    input_data_reshaped = input_data_as_numpy_array.reshape(1,-1)

    prediction = loaded_model.predict(input_data_reshaped)
    print(prediction)

    if (prediction[0] == 0):
      return 'Developing Country'
    elif (prediction[0] == 1):
      return 'Developed Country'
    else:
      return 'Under Developed Country'

def main():

    # giving a title
    st.title('Cluster Prediction')

    # getting the input data from the user
    Birth_Rate = st.text_input('Enter birth rate')
    Business_Tax_Rate = st.text_input('Enter tax Percentage')
    CO2_Emissions = st.text_input('CO2_Emissions')
    Days_to_Start_Business = st.text_input('Enter Number of days to start business')
    Ease_of_Business = st.text_input('Ease_of_Business')
    Energy_Usage = st.text_input('Total Energy Usage')
    GDP = st.text_input('Total GDP')
    Health_Exp_Per_GDP =st.text_input('Enter HEP GDP')
    Health_Exp_Capita = st.text_input('Total Health expenditure')
    Hours_to_do_Tax = st.text_input('Hours_to_do_Tax')
    Infant_Mortality_Rate = st.text_input('Infant_Mortality_Rate in Percentage')
    Internet_Usage = st.text_input('Average Internet_Usage')
    Lending_Interest = st.text_input('Lending_Interest')
    Life_Expectancy_Female = st.text_input('Life_Expectancy_Female')
    Life_Expectancy_Male = st.text_input('Life_Expectancy_Male')
    Mobile_Phone_Usage = st.text_input('Mobile_Phone_Usage')
    Population_0_14 = st.text_input('Total population between 0-14 in percentage')
    Population_15_64 = st.text_input('Total population between 15-64 in percentage')
    Population_65_and_above = st.text_input('Total population above 65 in percentage')
    Population_Total = st.text_input('Total population')
    Population_Urban = st.text_input('Urban population in percentage')
    Tourism_Inbound = st.text_input('$ earned in tourism')
    Tourism_Outbound = st.text_input('$ spent on tourism')

# code for Prediction
Predict = ''

# creating a button for Prediction
import streamlit as st
if st.button('Submit'):
  Predict = Cluster_prediction([Birth_Rate,Business_Tax_Rate,CO2_Emissions,Days_to_Start_Business, Ease_of_Business, Energy_Usage, GDP,Health_Exp_Per_GDP,Health_Exp_Capita, Hours_to_do_Tax,Infant_Mortality_Rate, Internet_Usage, Lending_Interest,Life_Expectancy_Female, Life_Expectancy_Male, Mobile_Phone_Usage, Population_0_14, Population_15_64,Population_65_and_above, Population_Total, Population_Urban,Tourism_Inbound, Tourism_Outbound])

  st.success(Predict)

if __name__ == '__main__':
  main()

samp = cluster_1_df.iloc[0:1, ]
samp = samp.append(cluster_2_df.iloc[0:1, ])
samp = samp.append(cluster_3_df.iloc[0:1, ])
samp

