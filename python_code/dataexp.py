%matplotlib inline
import numpy as np
import scipy as sp
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import pandas as pd
#import time
from collections import Counter
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 100)
pd.set_option('display.notebook_repr_html', True)
import seaborn as sns
sns.set_style("whitegrid")
sns.set_context("poster")
import json
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import math

os.chdir('/Users/stevenfelix/Dropbox/DataScience/Projects/PsychologyToday/Data/')
data = pd.read_pickle('therapist_profiles_clean_07-20.pkl')

with open("profiledict.json", "r") as fd:
    profiledict = json.load(fd)
with open("profilefeaturesdict_bool_dict.json", "r") as fd:
    featuresdict = json.load(fd)

################### Counts of Specialities, Issues, treatment orientations, and mental health #################
def plot_counts(dictinfo):
    i = 0
    c = 2
    r = int(math.ceil(len(dictinfo) / 2))
    fig = plt.figure(figsize = [20,25])
    for k in dictinfo:
        i += 1
        counter = Counter(dictinfo[k]['counts'])
        top = counter.most_common(20)
        y_pos = np.arange(len(top))
        newplt = fig.add_subplot(r,c,i)
        newplt.barh(y_pos, zip(*top)[1], align='center', alpha=0.7)
        newplt.set_yticks(y_pos);
        newplt.set_yticklabels(zip(*top)[0])
        newplt.set_xlabel('Number of providers endorsing')
        newplt.set_title(k)
    fig.subplots_adjust(wspace = .5)
    fig.suptitle("Top 20 most endorsed responses for 4 variables", fontsize="large")

plot_counts(profiledict)

####################### by region #####################

def compare_regions(variable,topnum):
    df = pd.DataFrame(featuresdict[variable])
    if u'' in df.columns:
        df = df.drop(u'',axis=1)
    top10 = df.sum().sort_values(ascending=False)[:topnum].index
    df_top10 = df[top10]
    df_top10 = df_top10.join(data.region)
    dflong = pd.melt(frame=df_top10, id_vars='region', value_vars=top10)
    #sns.factorplot(x ='region', y='value', col = 'variable', col_wrap=2, data = sp_long, kind = 'bar')
    g = sns.barplot(x ='variable', y='value', hue = 'region', data = dflong)
    g.set_xticklabels(top10, rotation = 45);

compare_regions('specialties',15) # northeast has selfesteem issues, mountain has trauma/PTSD
compare_regions('issues',15)
compare_regions('treatmentorientation',15)


#################### Clusters among providers ###############
def add_bool(data, category,variable = None, topnum = 10):
    """Joins to an existing dataframe either an entire boolean Dataframe (category) from featuredict,
    or a single boolean variable from one of the dataframes (categories)."""
    if variable is not None:
        series = pd.Series(featuresdict[category][variable])
        series.name = variable
        return data.join(series,rsuffix='2')
    else:
        df = pd.DataFrame(featuresdict[category])
        if u'' in df.columns:
            df = df.drop(u'',axis=1)
        top10 = df.sum().sort_values(ascending=False)[:topnum].index
        df_top10 = df[top10]
        return data.join(df_top10)


data.loc[:,'insurance'] = data.insurance.fillna('No').map({'Yes':1,'No':0})
data.loc[:,'graduated'] = data.graduated.astype(float)
#data.columns
orientation_df = data[['insurance']].dropna() # could also include years, fee, graduated
orientation_df = (add_bool(orientation_df, 'treatmentorientation')
                    .pipe(add_bool, 'specialties','depression'))
orientation_df = orientation_df.loc[orientation_df.depression == 1].drop('depression',axis=1)

orientation_df.columns
orientation_df.head()


issues_anxiety = issues_anxiety.loc[issues_anxiety.none ==0,:].drop(['none','anxiety2'], axis = 1)
issues_anxiety.shape

a = orientation_df.sum(axis=1) # total number of issues per provider
a[a == 0].count() # number of providers with no listed issues in their pro
#orientation_df['other'] = 0
#orientation_df.loc[a[a==0].index, 'other'] = 1
#Counter(orientation_df['other']) # should equal 7

ind = orientation_df.index
Z = linkage(orientation_df, method='complete', metric = 'dice')

plt.figure(figsize=(25, 10))
plt.title('Hierarchical Clustering Dendrogram')
plt.xlabel('sample index')
plt.ylabel('distance')
dendrogram(
    Z,
    truncate_mode='lastp',  # show only the last p merged clusters
    p=20,  # show only the last p merged clusters
    show_leaf_counts=True,  # otherwise numbers in brackets are counts
    #leaf_rotation=90.,
    leaf_font_size=20.,
    #show_contracted=True,  # to get a distribution impression in truncated branches
)
plt.show()

Z = linkage(orientation_df, method='complete', metric = 'jaccard')
k=10
clusters = fcluster(Z, k, criterion='maxclust')
jaccard_complete5 = Counter(clusters)
jaccard_complete10 = Counter(clusters)
dice_complete5 = Counter(clusters)
dice_complete10 = Counter(clusters)

pd.DataFrame({'jaccard':jaccard_complete5,'dice':dice_complete5}) # identical results
pd.DataFrame({'jaccard':jaccard_complete10,'dice':dice_complete10}) # identical results