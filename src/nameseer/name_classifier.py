
import sys
import unicodedata
import re

from pathlib import Path

import pickle
import pkg_resources

import numpy as np
from nltk import ngrams
from abydos.phonetic import Soundex, DoubleMetaphone
from pythainlp.soundex import soundex as th_soundex
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer

class NameClassifier():
	
	def __init__(self):
		super().__init__()

		self.dmp_encoder = DoubleMetaphone()
		self.soundex_encoder = Soundex()

		self.cat2idx = {}
		self.idx2cat = {}
		self.vectorizer = CountVectorizer(token_pattern='\S+', max_features=25000)
		self.clf = LogisticRegression(random_state=10, max_iter=1000)

		self.padding = False
		self.ch_feat = True
		self.ng_feat = True
		self.sd_feat = True  # soundex
		self.mp_feat = False # methaphone (not supporting thai yet)
		
	def config_options(self, config: str):
		opts = config.split(":")
		for opt in config.split(":"):
			if (opt == 'pad') or (opt == 'all'):
				self.padding = True
			if (opt == 'ng') or (opt == 'all'):
				self.ch_feat = True
			if (opt == 'ch') or (opt == 'all'):
				self.ng_feat = True
			if (opt == 'sd') or (opt == 'all'):
				self.sd_feat = True								
			if (opt == 'mp') or (opt == 'all'):
				self.mp_feat = True

	def _extract_ngram_feats(self, units):
		feats = []
		n_units = len(units)
		for i, u in enumerate(units):
			is_lastname = (i == (n_units-1))
			feats += self._token_ngram_feats(u, is_lastname)
		return feats
	
	def _extract_stat_feats(self, units):
		feats = []
		return feats

	def _extract_metaphone_feats(self, units):
		feats = []
		ngram_feats = []
		n_units = len(units)
		for i, u in enumerate(units):
			is_lastname = (i == (n_units-1))

			(a,b) = self.dmp_encoder.encode(u)
			feats += ["M0|" + a]
			ngram_feats += self._token_ngram_feats(a, is_lastname)
			if b != "":
				feats += ["M0|" + b]
				ngram_feats += self._token_ngram_feats(b, is_lastname)
		return feats + [("M|" + f) for f in ngram_feats]

	def _extract_soundex_feats(self, units):
		feats = []
		for u in units:
			#f = self.soundex_encoder.encode(u)
			f = th_soundex(u)
			feats += ["S|" + f]
		return feats

	# retract non-ascii characters
	def _extract_char_feats(self, name):
		feats = []
		chars = re.sub(r"[A-Z_ .-]+", "", name)
		for c in chars:
			feats += ["C|" + c]
		return feats

	def _token_ngram_feats(self, text, is_lastname):
		ngram_feats = []
		if is_lastname:
			text = "+" + text + "+"
		else:
			text = "$" + text + "$"
		for n in [2,3,4]:
			ngram_feats += self._word2ngrams(text, n)
		return ngram_feats

	def _word2ngrams(self, text, n=3):
		return [text[i:i+n] for i in range(len(text)-n+1)]

	def _deaccent(self, text):
		norm = unicodedata.normalize("NFD", text)
		result = ''.join(ch for ch in norm if unicodedata.category(ch) != 'Mn')
		return unicodedata.normalize("NFC", result) 

	def extract_feat_str(self, name: str):
		ascii_name = name
		ascii_name = re.sub(r"[-_']", " ", ascii_name)
		ascii_name = re.sub(r"^\\s+", "", ascii_name)
		units = ascii_name.split(" ")

		feats = []
		# chfeats, ngramfeats, mpfeats, sdfeats
		if self.ng_feat:
			ngramfeats = self._extract_ngram_feats(units)
			feats += ngramfeats
		if self.mp_feat:
			mpfeats = self._extract_metaphone_feats(units)
			feats += mpfeats
		if self.sd_feat:
			sdfeats = self._extract_soundex_feats(units)
			feats += sdfeats
		if self.ch_feat:
			chfeats = self._extract_char_feats(name)
			feats += chfeats

		return ' '.join(feats)
	
	# X: list of names
	# y: list of name classes
	def fit(self, names: list, cats: list):
		print('extracting features:')
		X = [self.extract_feat_str(n) for n in names]
		print('[DONE]')

		print('vectorize features:')
		self.vectorizer = CountVectorizer(token_pattern='\S+', max_features=25000)
		self.vectorizer.fit(X)
		X_vector = self.vectorizer.transform(X)

		self.cat2idx = {k: v for v, k in enumerate(set(cats))}
		self.idx2cat = {v:k for k, v in self.cat2idx.items()}
		y_vector = [self.cat2idx[y] for y in cats]
		print('[DONE]')

		print('fitting model:')
		self.clf = LogisticRegression(random_state=10, max_iter=1000)
		self.clf.fit(X_vector, y_vector)
		print('[DONE]')

		y_hat = self.clf.predict(X_vector)
		correct_count = np.sum((y_hat == y_vector))
		total_count = len(y_vector)
		return float(correct_count) / float(total_count)
	
	def classify_names(self, names: list):
		n_names = len(names)
		cats = [None] * n_names
		for i, n in enumerate(names):
			n = n.replace(' ', '_')
			f = self.extract_feat_str(n)
			X_vector = self.vectorizer.transform([f])
			y_hat = self.clf.predict(X_vector)[0]
			cats[i] = self.idx2cat[y_hat]
		return cats

	def classify_names_with_scores(self, names: list):
		n_names = len(names)
		cats = [None] * n_names
		scores  = [None] * n_names
		for i, n in enumerate(names):
			f = self.extract_feat_str(n)
			X_vector = self.vectorizer.transform([f])
			probs = self.clf.predict_proba(X_vector)[0]
			y_hat = np.argmax(probs)
			cats[i] = self.idx2cat[y_hat]
			scores[i]  = probs[y_hat]
		return cats, scores

	def name_classes(self):
		return sorted(self.cat2idx, key=self.cat2idx.get)

	# save 3 file for the model, 'nameseer_vec.pk', 'nameseer_lr.pk', 'nameseer_meta.pk'
	def save_model(self, filename):
		meta_file  = filename + '_meta.pk'
		vec_file   = filename + '_vec.pk'
		model_file = filename + '_model.pk'

		pickle.dump({
			'cat2idx': self.cat2idx,
			'idx2cat': self.idx2cat,
		}, open(meta_file, 'wb'))
		pickle.dump(self.vectorizer, open(vec_file, 'wb'))
		pickle.dump(self.clf, open(model_file, 'wb'))
		
	@classmethod
	def load_pretrained_model(cls, filename=None):
		if (filename is None):
			filename = 'nameseer'

		meta_file  = pkg_resources.resource_filename(__name__, filename + '_meta.pk')
		vec_file   = pkg_resources.resource_filename(__name__, filename + '_vec.pk')
		model_file = pkg_resources.resource_filename(__name__, filename + '_model.pk')
		
		nc = NameClassifier()
		nc.vectorizer = pickle.load(open(vec_file, 'rb'))
		nc.clf = pickle.load(open(model_file, 'rb'))

		meta = pickle.load(open(meta_file, 'rb'))
		nc.cat2idx = meta['cat2idx']
		nc.idx2cat = meta['idx2cat']

		return nc

