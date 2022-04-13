'''
https://www.machinelearningplus.com/nlp/topic-modeling-python-sklearn-examples/
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os
import sys
rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])
sys.path.append(rootpath)

from object import NewsCorpus
from newsutil import NewsIO, NewsPath
newsio = NewsIO()
newspath = NewsPath()

import itertools

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import GridSearchCV


def prepare_docs_for_lda(corpus, fname, do):
    try:
        global SAMPLE_SIZE
    except:
        pass

    if do:
        docs_for_lda = {}
        for article in corpus.iter_sampling(n=SAMPLE_SIZE):
            docs_for_lda[article.id] = ' '.join(list(itertools.chain(*article.nouns_stop)))

        newsio.save(_object=docs_for_lda, _type='data', fname_object=fname)

    else:
        docs_for_lda = newsio.load(_type='data', fname_object=fname)

    return docs_for_lda

def vectorize_docs(docs, fname, do):
    if do:
        vectorizer = CountVectorizer(analyzer='word', min_df=100)
        docs_vectorized = vectorizer.fit_transform(docs.values())

        newsio.save(_object=docs_vectorized, _type='data', fname_object=fname)

    else:
        docs_vectorized = newsio.load(_type='data', fname_object=fname)

    return docs_vectorized

def sparcity(data):
    data_dense = data.todense()
    return ((data_dense > 0).sum()/data_dense.size)*100


def init_lda_model(parameters):
    lda_model = LatentDirichletAllocation(learning_method=parameters.get('learning_method'),
                                            random_state=parameters.get('random_state'),
                                            batch_size=parameters.get('batch_size'),
                                            evaluate_every=parameters.get('evaluate_every'),
                                            n_jobs=parameters.get('n_jobs'),
                                            )

    return lda_model

def gridsearch(fname, do, **kwargs):
    if do:
        lda_model = kwargs.get('lda_model')
        parameters = kwargs.get('parameters')
        docs_vectorized = kwargs.get('docs')

        gs_model = GridSearchCV(lda_model, param_grid=parameters)
        gs_model.fit(docs_vectorized)

        newsio.save(_object=gs_model, _type='model', fname_object=fname)

    else:
        gs_model = newsio.load(_type='model', fname_object=fname)

    return gs_model


if __name__ == '__main__':
    ## Parameters
    SAMPLE_SIZE = 10000

    DO_PREPARE_DOCS_FOR_LDA = False
    DO_VECTORIZE = False
    DO_GRIDSEARCH = True

    LDA_PARAMETERS = {'learning_method': 'online',
                      'random_state': 42,
                      'batch_size': 128,
                      'evaluate_every': -1,
                      'n_jobs': -1,
                      }
    GS_PARAMETERS = {'n_components': [5, 10, 15, 20, 30, 50], #NUM_TOPICS
                     'learning_decay': [0.5, 0.7, 0.9],
                     'max_iter': [10, 100, 500],
                    }


    ## Filenames
    fname_docs_for_lda = f'docs_{SAMPLE_SIZE}.pk'
    fname_docs_vectorized = f'docs_vectorized_{SAMPLE_SIZE}.pk'
    fname_gs_model = f'lda_gs_model_{SAMPLE_SIZE}.pk'

    ## Data import
    print('============================================================')
    print('--------------------------------------------------')
    print('Load corpus')

    corpus = NewsCorpus(fdir_corpus=newspath.fdir_corpus)
    DOCN = len(corpus)
    print(f'  | Corpus: {DOCN:,}')

    print('--------------------------------------------------')
    print('Docs for LDA')

    docs_for_lda = prepare_docs_for_lda(corpus=corpus, fname=fname_docs_for_lda, do=DO_PREPARE_DOCS_FOR_LDA)
    print(f'  | {len(docs_for_lda):,} articles')

    print('--------------------------------------------------')
    print('Vectorization')

    docs_vectorized = vectorize_docs(docs=docs_for_lda, fname=fname_docs_vectorized, do=DO_VECTORIZE)
    data_sparcity = sparcity(data=docs_vectorized)
    print(f'  | Shape: {docs_vectorized.shape}')
    print(f'  | Sparcity: {data_sparcity:,.03f}')

    ## Topic modeling
    print('============================================================')
    print('--------------------------------------------------')
    print('Init LDA model')

    lda_model = init_lda_model(parameters=LDA_PARAMETERS)
    print(f'  | {lda_model}')

    print('--------------------------------------------------')
    print('Gridsearch')

    gs_model = gridsearch(fname=fname_gs_model, do=DO_GRIDSEARCH, lda_model=lda_model, parameters=GS_PARAMETERS, docs=docs_vectorized)

    print('--------------------------------------------------')
    print('Best model')

    lda_model_best = gs_model.best_estimator_
    print(f'  | Parameters: {gs_model.best_params_}')
    print(f'  | Log likelihood score: {gs_model.best_score_:,.03f}')
    print(f'  | Perplexity: {lda_model_best.perplexity(docs_vectorized)}')