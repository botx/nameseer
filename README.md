# nameseer ['name-seer'] - a Thai person name classifier

*nameseer* ('name-seer') is a python library for Thai name classification. It can determine whether a given name is a Thai person name or a Thai corporate name. *nameseer* uses linguistics features within the name to determine whether the name is a Thai person name or not. *nameseer* comes with a pre-trained model that was trained on 700,000 company names and 700,000 person names, with 0.994 accuracy when tested on 400,000 unseen names.

*nameseer* is based on the name-ethnicity classifier, orginally proposed here:
> Treeratpituk, Pucktada, and C. Lee Giles. "Name-ethnicity classification and ethnicity-sensitive name matching." Proceedings of the AAAI Conference on Artificial Intelligence. Vol. 26. No. 1. 2012.

> Paper URL : https://ojs.aaai.org/index.php/AAAI/article/download/8324/8183

# Requirements
* abydos
* scikit-learn
* nltk
* pythainlp
* python = 3.7.6+

# Installation

`nameseer` can be installed using `pip` 

```
pip install nameseer
```

# Usages

Once installed, you can use `nameseer` within your python code to classify whether a Thai name is a person name or a corporate name. 

```
>>> from nameseer import NameClassifier

>>> nc = NameClassifier.load_pretrained_model()
>>> nc.classify_names(['ประยุทธ์ จันทร์โอชา','แอดวานซ์อินโฟร์เซอร์วิส'])
['person', 'company']
```

## Citation

```
Treeratpituk, Pucktada (2022). Nameseer: a Thai person name classifier. Mar 29, 2022. See https://github.com/botx/nameseer
```

## Author
Pucktada Treeratpituk, Bank of Thailand (pucktadt@bot.or.th)

## License

This project is licensed under the Apache Software License 2.0 - see the [LICENSE](LICENSE) file for details

