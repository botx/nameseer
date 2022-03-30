from pathlib import Path
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from .name_classifier import NameClassifier

# dir_path = 'data/names'
def load_from_directory(dir_path: str):
    data_path  = Path(dir_path)
        
    names = []
    cats = []

    for file_path in data_path.glob('*'):
        with open(file_path, 'r', encoding="utf-8") as f:
            for line in f:
                name = line.strip()
                names += [name]
                cats += [file_path.name]
    return names, cats

def train_model(names: list, cats: list):
    nc = NameClassifier()
    train_acc = nc.fit(names, cats)

    cats_hat = nc.classify_names(names)
    print(classification_report(cats, cats_hat, 
        target_names=nc.name_classes()))

    return nc

def train_and_evaluate(names: list, cats: list):
    names_train, names_test, cats_train, cats_test = train_test_split(
        names, cats, test_size=0.3, random_state=10)

    nc = NameClassifier()
    train_acc = nc.fit(names_train, cats_train)

    cats_hat = nc.classify_names(names_test)

    correct_count = np.sum([(a==b) for a, b in zip(cats_test, cats_hat)])
    total_count = len(cats_test)
    test_acc = float(correct_count)/total_count

    print('train acc:', train_acc)
    print('test acc:', test_acc)
    print(classification_report(cats_test, cats_hat, 
        target_names=nc.name_classes()))
