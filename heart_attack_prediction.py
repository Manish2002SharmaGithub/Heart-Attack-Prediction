# -*- coding: utf-8 -*-
"""Heart_Attack_prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jH0cTsvkeUjlaQScX3pT_uYuSNRNCDfv
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report, accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn import tree
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV

import keras
from keras.models import Sequential
from keras.layers import Dense
from tensorflow.keras.optimizers import Adam, SGD, RMSprop
from keras.layers import Dropout
from keras import regularizers

import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('/content/heart.csv')

df.head()

df.info()

"""EDA"""

ax = sns.countplot(x="Sex", data=df,color='red')
for p in ax.patches:
   ax.annotate('{:.1f}'.format(p.get_height()), (p.get_x()+0.25, p.get_height()+0.01))
plt.show()

plt.figure(1, figsize=(10,10))
df['HeartDisease'].value_counts().plot.pie(autopct="%1.1f%%",colors = ( "#4CAF50", "blue"),labels = df['HeartDisease'].unique(), shadow = True)
plt.legend(title = "Heart Failure:")
plt.show()

# plot histograms for each numerical variable
df.hist(figsize = (20, 20),color='green')
plt.show()

def diagnostic_plots(df, variable,target):
    # The function takes a dataframe (df) and

    # Define figure size.
    plt.figure(figsize=(20, 4))

    # histogram
    plt.subplot(1, 4, 1)
    sns.histplot(df[variable], bins=30,color = 'r')
    plt.title('Histogram')


    # scatterplot
    plt.subplot(1, 4, 2)
    plt.scatter(df[variable],df[target],color = 'g')
    plt.title('Scatterplot')
    
    
    # boxplot
    plt.subplot(1, 4, 3)
    sns.boxplot(y=df[variable],color = 'b')
    plt.title('Boxplot')
    
    # barplot
    plt.subplot(1, 4, 4)
    sns.barplot(x = target, y = variable, data = df)   
    plt.title('Barplot')
    
    
    plt.show()

diagnostic_plots(df,'RestingBP','HeartDisease')

diagnostic_plots(df,'Cholesterol','HeartDisease')

diagnostic_plots(df,'MaxHR','HeartDisease')

diagnostic_plots(df,'Oldpeak','HeartDisease')

diagnostic_plots(df,'FastingBS','HeartDisease')

# We have only 0's and 1's in this feature.
df.FastingBS.value_counts()

diagnostic_plots(df,'Age','HeartDisease')

pd.crosstab(df.Age,df.HeartDisease).plot(kind="bar",figsize=(20,6),color= ['green','red'])
plt.title('Heart Disease Frequency for Ages')
plt.xlabel('Age')
plt.ylabel('Frequency')
plt.show()

plt.figure(figsize=(10,4))
g = sns.countplot(data=df, x='HeartDisease', hue='Sex',color='orange')
plt.title('Sex distribution')
plt.show()

def detect_outliers(df,features):
    df_copy = df.drop(df[(df[features] == 0)].index)
    # 1st quartile
    q1 = df_copy[features].quantile(0.25)
    # 3rd quartile
    q3 = df_copy[features].quantile(0.75)
    iqr = q3-q1
    Lower_tail = q1 - 1.5 * iqr
    Upper_tail = q3 + 1.5 * iqr
    outlier_list_col = df_copy[(df_copy[features] >= Upper_tail) | (df_copy[features] <= Lower_tail)]  # | means "or"
    return pd.DataFrame(outlier_list_col)

RestingBP_outlier = detect_outliers(df,'RestingBP')
RestingBP_outlier.value_counts(RestingBP_outlier['HeartDisease'])

Cholesterol_outlier = detect_outliers(df,'Cholesterol')
Cholesterol_outlier.value_counts(Cholesterol_outlier['HeartDisease'])

imputer = SimpleImputer(strategy='median')

# We fit the imputer to the train set.
# The imputer will learn the median of all variables.
cols_to_use = ['Cholesterol','RestingBP']
imputer.fit(df[cols_to_use])

df[cols_to_use] = imputer.transform(df[cols_to_use])

df.ChestPainType.value_counts()

df.isna().sum()

df['AgeGroup']= np.nan
df.loc[(df['Age']>=28) & (df['Age']<35),'AgeGroup']='Young Adult' 
df.loc[(df['Age']>=35) & (df['Age']<=64),'AgeGroup']='Adult'
df.loc[df['Age']>64,'AgeGroup']='Seniors'

plt.figure(figsize=(10,4))
g=sns.countplot(data=df, x='AgeGroup', hue='HeartDisease', order=['Young Adult','Adult','Seniors'],color='yellow')
plt.title('Age group distribution')
plt.show()

df.drop(['Age'], axis=1, inplace=True)

catcols = ['Sex', 'ChestPainType','FastingBS','RestingECG',
            'ExerciseAngina',  'ST_Slope','AgeGroup']

def Label_Encoding(df,feature):
    label_encoder = LabelEncoder()
    df[feature]= label_encoder.fit_transform(df[feature])

for i in catcols:
    Label_Encoding(df,i)

df.head()

numcols  = ['RestingBP','Cholesterol','MaxHR']

scaler = StandardScaler()

# Scale data
df[numcols] = scaler.fit_transform(df[numcols])

"""Train test split"""

# Set up X and y variables
y, X = df['HeartDisease'], df.drop(columns='HeartDisease')

# Split the data into training and test samples
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

"""PREDICTION"""

logreg = LogisticRegression()

logreg.fit(X_train,y_train)

y_pred = logreg.predict(X_test)

logregAcc = accuracy_score(y_test,y_pred)
logregAcc

cm = confusion_matrix(y_test,y_pred)
conf_matrix=pd.DataFrame(data=cm,columns=['Predicted:0','Predicted:1'],index=['Actual:0','Actual:1'])
plt.figure(figsize = (8,5))
sns.heatmap(conf_matrix, annot=True,fmt='d')

"""KNN"""

# Building a model using KNeighborsClassifier 
knn = KNeighborsClassifier(n_neighbors = 5)

knn.fit(X_train, y_train)

y_pred = knn.predict(X_test)

knnAcc = accuracy_score(y_test,y_pred)
knnAcc

cm = confusion_matrix(y_test,y_pred)
conf_matrix=pd.DataFrame(data=cm,columns=['Predicted:0','Predicted:1'],index=['Actual:0','Actual:1'])
plt.figure(figsize = (8,5))
sns.heatmap(conf_matrix, annot=True,fmt='d')

"""Decision Tree"""

# Building Decision Tree model 
clf = tree.DecisionTreeClassifier(random_state=0)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)

clfAcc = accuracy_score(y_test,y_pred)
clfAcc

cm = confusion_matrix(y_test,y_pred)
conf_matrix=pd.DataFrame(data=cm,columns=['Predicted:0','Predicted:1'],index=['Actual:0','Actual:1'])
plt.figure(figsize = (8,5))
sns.heatmap(conf_matrix, annot=True,fmt='d')

"""SVM"""

svm = SVC(random_state=1)
svm.fit(X_train,y_train)

y_pred = svm.predict(X_test)

svmAcc = accuracy_score(y_test,y_pred)
svmAcc

cm = confusion_matrix(y_test,y_pred)
conf_matrix=pd.DataFrame(data=cm,columns=['Predicted:0','Predicted:1'],index=['Actual:0','Actual:1'])
plt.figure(figsize = (8,5))
sns.heatmap(conf_matrix, annot=True,fmt='d')

data={'Estimators':['Logistic Regression', 'K-Nearest Neighbor', 'Decision Tree','Support Vector Machine'],
      'Accuracy':[logregAcc,knnAcc,clfAcc,svmAcc]}

data =pd.DataFrame(data)

data.sort_values('Accuracy', ascending=False)

