#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os
import sys
rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])
sys.path.append(rootpath)

from newsutil import NewsPath, NewsIO, NewsFunc
newspath = NewsPath()
newsio = NewsIO()
newsfunc = NewsFunc()

import pickle as pk
from collections import defaultdict


if __name__ == '__main__':
    ## URLs
    print('============================================================')
    print('URLs')

    flist_url = os.listdir(newspath.fdir_url_list)
    query2date = defaultdict(list)
    for fname_url in flist_url:
        query, date = newsfunc.parse_fname_url_list(fname_url)
        query2date[query].append(date)

    print('  | fdir: {}'.format(newspath.fdir_url_list))
    for query in query2date.keys():
        url_date_list = list(sorted([date for date in query2date[query]], reverse=False))

        print('--------------------------------------------------')
        print('    | query     : {}'.format(query))
        print('    | start date: {}'.format(url_date_list[0]))
        print('    | end date  : {}'.format(url_date_list[-1]))
        print('    | # of dates: {:,}'.format(len(query2date[query])))

    ## Articles
    print('============================================================')
    print('Articles')

    article_count = 0
    for fname_url in flist_url:
        fpath_url = os.path.join(newspath.fdir_url_list, fname_url)
        with open(fpath_url, 'rb') as f:
            article_count += len(pk.load(f))

    flist_article = []
    fsize_total_article = 0
    for path, dirs, files in os.walk(newspath.fdir_article):
        for f in files:
            fpath = os.path.sep.join((path, f))
            flist_article.append(fpath)
            fsize_total_article += os.path.getsize(fpath)

    print('  | fdir: {}'.format(newspath.fdir_article))
    print('  | # of articles(ready): {:,}'.format(article_count))
    print('  | # of articles(done) : {:,}'.format(len(flist_article)))
    print('  | total filesize      : {:,.02f} MB ({:,.02f} GB)'.format(fsize_total_article/(1024**2), fsize_total_article/(1024**3)))

    ## Corpus
    print('============================================================')
    print('Corpus')

    for fdir in sorted(os.listdir(os.path.sep.join((newspath.fdir_corpus, 'Q-건설')))):
        print('  | {}: {:>7,d} articles'.format(fdir, len(os.listdir(os.path.sep.join((newspath.fdir_corpus, 'Q-건설', fdir))))))