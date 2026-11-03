import pandas as pd, numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate, GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, f1_score, recall_score

R="/home/hendra/projects/pkmGlico/ml_pipeline/src/data/dummy/generated_data.csv"
d=pd.read_csv(R); F=["glucose_saliva","ph_value","fructosamine_umol_l"]
X,y=d[F],d.bg_class
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.2,stratify=y,random_state=42)
cv=StratifiedKFold(5,shuffle=True,random_state=42)
P=lambda m: make_pipeline(StandardScaler(),m)
models={
 "TunedSVC_RBF":GridSearchCV(P(SVC(kernel="rbf")),{"svc__C":[0.1,1,10,100,1000],"svc__gamma":[0.01,0.03,0.1,0.3,1]},cv=cv,scoring="f1_macro"),
 "SVC_RBF":P(SVC(kernel="rbf")),
 "LogisticRegression":P(LogisticRegression(max_iter=1000)),
 "KNeighbors":P(KNeighborsClassifier()),
 "RandomForest":RandomForestClassifier(random_state=42),
 "GradientBoosting":GradientBoostingClassifier(random_state=42),
 "Dummy":DummyClassifier(strategy="most_frequent"),
}
rows=[]
for n,m in models.items():
    c=cross_validate(m,Xtr,ytr,cv=cv,scoring=["accuracy","f1_macro"],return_train_score=True)
    m.fit(Xtr,ytr); p=m.predict(Xte); ptr=m.predict(Xtr)
    rows.append(dict(model=n,cv_acc=c["test_accuracy"].mean(),cv_acc_std=c["test_accuracy"].std(),
     cv_f1=c["test_f1_macro"].mean(),train_acc=accuracy_score(ytr,ptr),test_acc=accuracy_score(yte,p),
     test_f1=f1_score(yte,p,average="macro"),rec_diab=recall_score(yte,p,labels=[2],average=None)[0],
     fn_diab_to_norm=int(((yte==2)&(p==0)).sum())))
    if n=="TunedSVC_RBF": print("best",m.best_params_)
o=pd.DataFrame(rows).sort_values("cv_f1",ascending=False)
pd.set_option("display.width",200); print(len(Xtr),len(Xte)); print(o.round(3).to_string(index=False))
o.to_csv("cls_comparison_table.csv",index=False)
