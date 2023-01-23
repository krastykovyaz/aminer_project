from sklearn.feature_extraction.text import TfidfVectorizer
import nltk, string
import pandas as pd
nltk.download('punkt')

import json
import psycopg2 as pg2


con = pg2.connect(host='aminer_postgres_db',
                  user='aminer',
                  password='team13best',
                  database='aminer_db')

con.autocommit = True
cur = con.cursor()

def get_papers_df():
    q = '''select * from papers'''
    return pd.read_sql(q, con)

def get_author_id(auth_id):
    q = f'''select paper_id from author_paper
    where author_id='{auth_id}' '''
    return pd.read_sql(q, con)

def get_top_author_ids(auth_ids):
    q = f'''select author_id, paper_id from author_paper
    where paper_id in {auth_ids}'''
    return pd.read_sql(q, con)


stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

def get_top_k_collaborators_by_author(author_id: int, top_k = 3) -> list:
    author_id = list(get_author_id(author_id)['paper_id'])[0]
    # print(author_id_, type(author_id_))
    # Tokenize data
    # df_papers = pd.read_csv('../data/data_csv/sampled_papers_22.csv', sep='\t', index_col='id')
    df_papers = get_papers_df()
    df_papers.set_index('id', inplace=True)
    map_keys = {k:i  for i,k in zip(df_papers.abstract.index, range(len(df_papers.abstract.index)))}
    corpus = df_papers.abstract
    vect = TfidfVectorizer(tokenizer=normalize, stop_words='english')
    tfidf = vect.fit_transform(corpus)   
    # Get list of similarities                                                                                                                                                                                                                    
    pairwise_similarity = tfidf * tfidf.T
    collector = {}
    for item in pairwise_similarity:
        map_list = [(k,v) for k,v in zip(item.indices, item.data)]
        similar = [(map_keys[item[0]], item[1]) for item in map_list if 0.1 < item[1] < 0.99]
        if len(item.indices) > 0:
            collector[map_keys[item.indices[-1]]] = similar

    # Choose some title
    tit = df_papers.loc[author_id].title
    call = df_papers[df_papers.title==tit].index[0]
    book_list = collector[call]
    book_list.sort(key=lambda x:x[1], reverse=True)
    # Get recomedation by n_citation and similarity
    idx = [itm[0] for itm in book_list]
    map_similar = {itm[0]:itm[1] for itm in book_list}
    df_local = df_papers[df_papers.index.isin(idx)]
    df_local.loc[:,'similarity'] = [map_similar[it] for it in df_local.index]
    df_local = df_local.loc[df_local.index.isin(idx)].sort_values(['n_citation', 'similarity'])[::-1]
    sort_papers = list(df_local.iloc[:top_k].index)
    sort_papers_t = tuple(id_ for id_ in sort_papers)
    df_auth_pap = get_top_author_ids(sort_papers_t)
    dict_auth_pap = {k:v for k,v in zip(df_auth_pap['paper_id'],df_auth_pap['author_id'])}
    return [dict_auth_pap[p] for p in sort_papers][:top_k]


def get_top_k_papers_by_author(author_id: int, top_k = 3) -> list:
    author_id = list(get_author_id(author_id)['paper_id'])[0]
    # print(author_id_, type(author_id_))
    # Tokenize data
    # df_papers = pd.read_csv('../data/data_csv/sampled_papers_22.csv', sep='\t', index_col='id')
    df_papers = get_papers_df()
    df_papers.set_index('id', inplace=True)
    map_keys = {k:i  for i,k in zip(df_papers.abstract.index, range(len(df_papers.abstract.index)))}
    corpus = df_papers.abstract
    vect = TfidfVectorizer(tokenizer=normalize, stop_words='english')
    tfidf = vect.fit_transform(corpus)   
    # Get list of similarities                                                                                                                                                                                                                    
    pairwise_similarity = tfidf * tfidf.T
    collector = {}
    for item in pairwise_similarity:
        map_list = [(k,v) for k,v in zip(item.indices, item.data)]
        similar = [(map_keys[item[0]], item[1]) for item in map_list if 0.1 < item[1] < 0.99]
        if len(item.indices) > 0:
            collector[map_keys[item.indices[-1]]] = similar

    # Choose some title
    tit = df_papers.loc[author_id].title
    call = df_papers[df_papers.title==tit].index[0]
    book_list = collector[call]
    book_list.sort(key=lambda x:x[1], reverse=True)
    # Get recomedation by n_citation and similarity
    idx = [itm[0] for itm in book_list]
    map_similar = {itm[0]:itm[1] for itm in book_list}
    df_local = df_papers[df_papers.index.isin(idx)]
    df_local.loc[:,'similarity'] = [map_similar[it] for it in df_local.index]
    df_local = df_local.loc[df_local.index.isin(idx)].sort_values(['n_citation', 'similarity'])[::-1]
    return list(df_local.iloc[:top_k].index)

# 864128
if __name__=='__main__':
    print(get_top_k_collaborators_by_author(2506, 3))
    print(get_top_k_papers_by_author(2506, 3))
