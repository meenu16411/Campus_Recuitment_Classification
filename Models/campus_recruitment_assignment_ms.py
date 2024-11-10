# -*- coding: utf-8 -*-
"""Campus_Recruitment_Assignment_MS

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1TXSum-UBEeHDuYLfe0KY2gc1Av8FzRCl
"""

# import necessary modules
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import GridSearchCV

# mount google drive
from google.colab import drive
drive.mount('/content/drive')

# load campus recruitment data
df=pd.read_csv('/content/drive/MyDrive/Campus_Recruitment_Data.csv')

nrows,ncols=df.shape
print(f"Number of rows {nrows} \nNumber of columns {ncols}")

# print dataset

df.head()

# renameing and removing unnecessary columns
df.rename(columns={'Communication Skill Rating':'communi_rating','Workshops/Certificatios':'workshops'},inplace=True)
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# checking for data type of columns in df
df.dtypes

# statical summary of data
df.describe()

# check Missing values
print("\nMissing Values Check:")
print(df.isnull().sum())

# Encoding categorical features
le = preprocessing.LabelEncoder()
df['Internship'] = le.fit_transform(df['Internship'])
df['Hackathon'] = le.fit_transform(df['Hackathon'])
df['PlacementStatus'] = le.fit_transform(df['PlacementStatus'])  # Placed=1, NotPlaced=0

df.head()

# check for duplicates
nduplicates=df.duplicated().sum()

if nduplicates>0:
  print("There are nduplicates rows in the dataset")
else:
  print("There are no duplicate rows in the dataset")

# check unique values in each column
for i in df.columns:
    print(f"{i} : {df[i].unique()}")

# Histogram of Internship
df["Internship"].plot(kind='hist')

df["PlacementStatus"].plot(kind='hist')
# ALmost 45% students are not placed

# checking for correlation between the features
df.corr()['PlacementStatus']

"""Factors Influencing Placement Status



Positive Correlates:

Skills, Internships, 10th Percentage, and Workshops: These factors exhibit a moderate positive correlation with placement status, suggesting that they positively influence a candidate's chances of securing a placement.
Salary: This factor demonstrates a strong positive correlation with placement status, indicating that higher salary offers are often associated with successful placements.
Negative Correlate:

Backlogs: Backlogs have a strong negative correlation with placement status, implying that a higher number of backlogs can significantly diminish placement prospects.
Moderate Correlates:

CGPA and Communication Rating: While these factors also have a moderate positive impact on placement, their influence is less pronounced compared to skills, internships, or workshops.
These findings underscore the importance of a well-rounded profile, encompassing both academic performance and practical experience, in securing desirable placements.
"""

corr_matrix = df.corr()

# 2. Plot a correlation matrix
plt.figure(figsize=(12, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', linewidths=0.5, linecolor='black')
plt.title('Correlation Matrix of Numerical Features')
plt.show()

# pair plot for relationship of  each feature with the PlacementStatus
sns.pairplot(df, diag_kind='kde', hue='PlacementStatus', palette='coolwarm')
plt.suptitle('Pair Plot of Features', y=1.02)
plt.show()

# Count plot for Internship vs PlacementStatus
plt.figure(figsize=(12, 4))
sns.countplot(x='Internship', hue='PlacementStatus', data=df, palette='viridis')
plt.title('Internship vs PlacementStatus')
plt.show()

# Count plot for Hackathon vs PlacementStatus
sns.countplot(x='Hackathon', hue='PlacementStatus', data=df, palette='viridis')
plt.title('Hackathon vs PlacementStatus')
plt.show()

# Distribution of CGPA for students got  Placed vs Not Placed
plt.figure(figsize=(8, 6))
sns.histplot(df[df['PlacementStatus'] == 1]['CGPA'], label='Placed', color='green', kde=True, stat="density", bins=20)
sns.histplot(df[df['PlacementStatus'] == 0]['CGPA'], label='Not Placed', color='red', kde=True, stat="density", bins=20)
plt.title('CGPA Distribution for Placed vs Not Placed Students')
plt.legend()
plt.show()

# Distribution of  backlogs for students got Placed vs Not Placed
plt.figure(figsize=(8, 6))
sns.histplot(df[df['PlacementStatus'] == 1]['backlogs'], label='Placed', color='blue', kde=True, stat="density", bins=20)
sns.histplot(df[df['PlacementStatus'] == 0]['backlogs'], label='Not Placed', color='red', kde=True, stat="density", bins=20)
plt.title('backlogs Distribution for Placed vs Not Placed Students')
plt.legend()
plt.show()

# Bar plot for average CGPA of placed vs not placed students
sns.barplot(x='PlacementStatus', y='backlogs',hue ='Internship', data=df, palette='coolwarm')
plt.title('Average CGPA by PlacementStatus')
plt.show()

"""**Backlog** is the most influential factor for the placement."""

plt.figure(figsize=(8, 6))
sns.histplot(df[df['PlacementStatus'] == 1]['Mini Projects'], label='Placed', color='blue', kde=True, stat="density", bins=20)
sns.histplot(df[df['PlacementStatus'] == 0]['Mini Projects'], label='Not Placed', color='red', kde=True, stat="density", bins=20)
plt.title('Mini Projects Distribution for Placed vs Not Placed Students')
plt.legend()
plt.show()

# Bar plot for average CGPA for placed vs not placed students
sns.barplot(x='PlacementStatus', y='CGPA', data=df)
plt.title('Average CGPA by PlacementStatus')
plt.show()

sns.barplot(x='PlacementStatus', y='Hackathon', data=df, palette='coolwarm')
plt.title('Average Hackathon by PlacementStatus')
plt.show()

sns.barplot(x='PlacementStatus', y='Internship', data=df, palette='coolwarm')
plt.title('Average Internship by PlacementStatus')
plt.show()

# Dropping irrelevant columns from X
x=df.drop(['StudentId','PlacementStatus','salary'],axis=1)

x.shape

y = df['PlacementStatus']

y

# split data into test and train
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.3, random_state = 42)

"""# Hyperparameter tuning, cross validation and model evaluation"""

# parameters for random forest
param_grid_rf = {
    'n_estimators': [50, 100, 200],
    'max_depth': [10, 20, 30, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

# parameters for Decision tree
param_grid_dt = {
    'criterion': ['gini', 'entropy'],
    'max_depth': [10, 20, 30, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

# parameters for KNeighbors
param_grid_knn = {
    'n_neighbors': [3, 5, 7, 9],
    'weights': ['uniform', 'distance'],
    'metric': ['euclidean', 'manhattan', 'minkowski']
}

# Initialize the models
rf = RandomForestClassifier()
dt = DecisionTreeClassifier()
knn = KNeighborsClassifier()

grid_rf = GridSearchCV(estimator=rf, param_grid=param_grid_rf, cv=5, scoring='accuracy', verbose=1)
grid_dt = GridSearchCV(estimator=dt, param_grid=param_grid_dt, cv=5, scoring='accuracy', verbose=1)
grid_knn = GridSearchCV(estimator=knn, param_grid=param_grid_knn, cv=5, scoring='accuracy', verbose=1)

grid_rf.fit(x_train, y_train)
ypred=grid_rf.predict(x_test)

grid_dt.fit(x_train, y_train)
ypred=grid_dt.predict(x_test)

grid_knn.fit(x_train, y_train)
ypred=grid_knn.predict(x_test)

# Printing best parameters
print("Best parameters for Random Forest: ", grid_rf.best_params_)
print("Best parameters for DecisionTreeClassifiert: ", grid_dt.best_params_)
print("Best parameters for KNeighborsClassifier: ", grid_knn.best_params_)

# Using best estimators for final classification
rf_best = grid_rf.best_estimator_
dt_best = grid_dt.best_estimator_
knn_best = grid_knn.best_estimator_

# Classification using best parameters of RFC
classify = RandomForestClassifier(max_depth=10, min_samples_leaf=1, min_samples_split=2, n_estimators=100)
classify.fit(x_train, y_train)
y_pred=classify.predict(x_test)

ypred

accuracy_score=metrics.accuracy_score(y_test,ypred)

accuracy_score

# Confusion Matrix
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, ypred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title(f'Confusion Matrix for random forest')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

"""**True Negatives (TN)** = 1530
The model correctly predicted 1530 instances as Negative (when they were actually Negative).

**False Positives (FP)** = 244
The model incorrectly predicted 244 instances as Positive (when they were actually Negative). This is also known as a Type I error.

**False Negatives (FN)** = 96
The model incorrectly predicted 96 instances as Negative (when they were actually Positive). This is also known as a Type II error.

**True Positives (TP)** = 1130
The model correctly predicted 1130 instances as Positive (when they were actually Positive).
"""

classification_report=metrics.classification_report(y_test,ypred,output_dict=True)

report_df = pd.DataFrame(classification_report).transpose()

# heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(report_df.iloc[:-1, :-1], annot=True, cmap="coolwarm", linewidths=0.5)
plt.title('Classification Report Heatmap')
plt.show()

# classification_report
accuracy = classification_report['accuracy']  # Overall accuracy
precision = classification_report['weighted avg']['precision']  # Weighted precision
recall = classification_report['weighted avg']['recall']  # Weighted recall
f1_score = classification_report['weighted avg']['f1-score']  # Weighted F1-score
print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1-Score: {f1_score}")

importances = RandomForestClassifier.feature_importances_

ypred_pob=classify.predict_proba(x_test)[:, 1]
fpr, tpr, thresholds = metrics.roc_curve(y_test, ypred_pob)
roc_auc = metrics.auc(fpr, tpr)
roc_auc

ypred_pob

roc_auc = metrics.auc(fpr,tpr)
roc_auc

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' %roc_auc )
plt.plot([0, 1], [0, 1], 'k--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate (FPR)')
plt.ylabel('True Positive Rate (TPR)')
plt.title('ROC Curve for Random Forest Classifier (Placement Opportunities)')
plt.legend(loc="lower right")
plt.grid(True)
plt.show()

knn=KNeighborsClassifier(metric='manhattan', n_neighbors= 5, weights='distance')

knn.fit(x_train,y_train)

ypred=knn.predict(x_test)

ypred

accuracy_score=metrics.accuracy_score(y_test,ypred)

accuracy_score

# Confusion Matrix
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, ypred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title(f'Confusion Matrix for kNeighboursClassifier')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

classification_report=metrics.classification_report(y_test,ypred,output_dict=True)

report_df = pd.DataFrame(classification_report).transpose()

# heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(report_df.iloc[:-1, :-1], annot=True, cmap="coolwarm", linewidths=0.5)
plt.title('Classification Report Heatmap')
plt.show()

# classification_report of K-nearest neighbours
accuracy = classification_report['accuracy']  # Overall accuracy
precision = classification_report['weighted avg']['precision']  # Weighted precision
recall = classification_report['weighted avg']['recall']  # Weighted recall
f1_score = classification_report['weighted avg']['f1-score']  # Weighted F1-score
print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1-Score: {f1_score}")

# Classifying with best parameters of Decision tree classifier
clf=DecisionTreeClassifier(criterion='gini', max_depth= 10, min_samples_leaf= 4, min_samples_split= 10)

clf.fit(x_train,y_train)

ypred=clf.predict(x_test)

accuracy_score=metrics.accuracy_score(y_test,ypred)

accuracy_score

# Confusion Matrix
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, ypred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title(f'Confusion Matrix for Decision Tree')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

classification_report=metrics.classification_report(y_test,ypred,output_dict=True)

report_df = pd.DataFrame(classification_report).transpose()

# heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(report_df.iloc[:-1, :-1], annot=True, cmap="coolwarm", linewidths=0.5)
plt.title('Classification Report Heatmap')
plt.show()

# classification_report of Decision Tree Classifier
accuracy = classification_report['accuracy']  # Overall accuracy
precision = classification_report['weighted avg']['precision']  # Weighted precision
recall = classification_report['weighted avg']['recall']  # Weighted recall
f1_score = classification_report['weighted avg']['f1-score']  # Weighted F1-score
print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1-Score: {f1_score}")

"""
 # Voting Classifier using Random Forest, Decision Tree and K-nearest neighbours"""

# hard voting classifier
voting_clf = VotingClassifier(estimators=[
    ('rf', rf_best),
    ('dt', dt_best),
    ('knn', knn_best)], voting='hard')

# training the Voting Classifier
voting_clf.fit(x_train, y_train)

# make classifications
ypred_voting = voting_clf.predict(x_test)

ypred_voting

y_test

#  accuracy score of the Voting Classifier
voting_accuracy = metrics.accuracy_score(y_test, ypred_voting)
print(f"Voting Classifier Accuracy: {voting_accuracy}")

classification_report_voting = metrics.classification_report(y_test, ypred_voting)
print("Classification Report for Voting Classifier:\n", metrics.classification_report(y_test, ypred_voting))

# confusion matrix for Voting Classifier
confusion_voting = metrics.confusion_matrix(y_test, ypred_voting)
print(f"Confusion Matrix for Voting Classifier:\n {confusion_voting}")

# plotting Confusion Matrix heatmap for Voting Classifier
plt.figure(figsize=(8, 6))
sns.heatmap(confusion_voting, annot=True, cmap="coolwarm", fmt='d', linewidths=0.5)
plt.title('Confusion Matrix Heatmap - Voting Classifier')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# comparing  performance with individual models
print(f"Random Forest Accuracy: {metrics.accuracy_score(y_test, rf_best.predict(x_test))}")
print(f"Decision Tree Accuracy: {metrics.accuracy_score(y_test, dt_best.predict(x_test))}")
print(f"KNN Accuracy: {metrics.accuracy_score(y_test, knn_best.predict(x_test))}")
print(f"Voting Classifier Accuracy: {voting_accuracy}")

# classification reports for individual models models
print("Random Forest Classification Report:\n", metrics.classification_report(y_test, rf_best.predict(x_test)))
print("Decision Tree Classification Report:\n", metrics.classification_report(y_test, dt_best.predict(x_test)))
print("KNN Classification Report:\n", metrics.classification_report(y_test, knn_best.predict(x_test)))