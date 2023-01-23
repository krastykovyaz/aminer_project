from argparse import ArgumentParser
from copy import copy
import fasttext
import gc
import numpy as np
import os
import pandas as pd
import re
from scipy.spatial.distance import cosine
from sklearn.metrics import pairwise_distances
from tqdm import tqdm
import yaml

        
def IoU(x, y):
    if len(x) > 0: 
        return len(y.intersection(x)) / len(x) 
    return 0

def get_run_args():
    parser = ArgumentParser(description='Find clusters')
    parser.add_argument('--input-file', type=str)
    parser.add_argument('--config-file', type=str)
    parser.add_argument('--model-file', type=str)
    parser.add_argument('--output-file', type=str)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_run_args()
    
    with open(args.config_file, 'r') as config:
        parameters = yaml.safe_load(config)
    
    locals().update(parameters)

#     obscene_corpus = pd.read_csv(os.path.join("./datasets/",'obscene_corpus.txt'), sep='\t', engine='python', encoding='utf8')
#     obsene_words = obscene_corpus['word'].apply(lambda x: x.lower())

#     stop_words_all = []
#     file_names = ['stopwords_nltk.txt', 'stopwords.txt', 'RussianStopWords.txt']
#     for file_name in file_names:
#         with open(os.path.join("./datasets/", file_name), encoding='utf8') as f:
#             stop_words = f.read().split("\n")
#         if file_name == 'stopwords_nltk.txt':
#             stop_words = stop_words[0][1:-1].replace('"', "").split(", ")
#         stop_words_all.extend(stop_words)
#     stop_words_all.extend(VERBS)
#     stop_words_all.extend(EXTRA_STOP_WORDS)
#     stop_words_all.extend(obsene_words)
#     stop_words_all = list(set(stop_words_all))

#     for word in WORDS_TO_REMOVE:
#         stop_words_all.remove(word)

    with open(STOP_WORDS_FILE, encoding='utf8') as f:
        stop_words_all = f.read().split("\n")
    if '' in stop_words_all:
        stop_words_all.remove('')
    
    if args.input_file.split('.')[1] == 'csv':
        dataset = pd.read_csv(os.path.join(INPUT_DIR, args.input_file), sep=';') 
    elif args.input_file.split('.')[1] == 'xlsx': 
        dataset = pd.read_excel(os.path.join(INPUT_DIR, args.input_file), engine='openpyxl') 
    else:
        print('Wrong input file format')

    if FILTER_TNO:
        dataset = dataset[dataset[TOPIC_COL] == "Тематика не определена"].reset_index(drop=True)

    dataset[TEXT_COL] = dataset[RAW_TEXT_COL].copy()
    dataset[TEXT_COL] = dataset[TEXT_COL].apply(lambda x: str(x).replace("_x001A_",""))
    dataset[TEXT_COL] = dataset[TEXT_COL].apply(lambda x: re.sub("[0-9!№\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]","", str(x).lower()))
    dataset[TEXT_COL] = dataset[TEXT_COL].apply(lambda x: " ".join([word for word in x.lower().split() if word not in stop_words_all]))
    
    
    if not os.path.exists(os.path.join(INPUT_DIR, PHRASES_FILE)):
        text_unique = [x.lower() for x in dataset[TEXT_COL].values]
        with open(os.path.join(INPUT_DIR, PHRASES_FILE), 'w', encoding='utf8') as the_file:
            for row in text_unique:
                the_file.write(row+'\n')

    if os.path.exists(os.path.join(INPUT_DIR, MODEL_FILE)):
        fasttext_model = fasttext.load_model(os.path.join(INPUT_DIR, MODEL_FILE))
    else:        
        fasttext_model = fasttext.train_unsupervised(input=os.path.join(INPUT_DIR, MODEL_FILE),
                                            model='skipgram',
                                            thread=FASTTEXT_N_THREADS,
                                            min_count=1,
                                            epoch=N_EPOCH,
                                            dim=DIM)

        fasttext_model.save_model(os.path.join(INPUT_DIR, MODEL_FILE))
    
    embeddings = np.vstack(dataset[TEXT_COL].apply(lambda x: fasttext_model.get_sentence_vector(x)))
    distance_matrix = 1 - pairwise_distances(embeddings, metric='cosine')
    
    dataset['thres_top'] = list(map(lambda x: np.where((x >= THRESHOLD) & (x < 1))[0], distance_matrix))
    dataset['thres_top_len'] = dataset['thres_top'].apply(lambda x: len(x))
    dataset['sets'] = dataset['thres_top'].apply(set)
    
    dataset['cluster'] = -1
    dataset.loc[dataset['thres_top_len'] < 2,'cluster'] = -2
    indices = dataset['thres_top_len'].sort_values(ascending=False).index.tolist()

    cluster_id = 0
    for i in tqdm(indices):
        if dataset.loc[i, 'cluster'] == -1:
            cluster_id += 1
            dataset.loc[i, 'cluster'] = cluster_id
            candidates_lst = dataset.loc[i, 'thres_top']
            if len(candidates_lst) < MIN_NEIGHBOR_N:
                break
            candidates_set = set(candidates_lst)
            dataset['common_proportion'] = dataset['sets'].apply(lambda x: IoU(x, candidates_set))
            dataset.loc[np.where((dataset['common_proportion'] >= THRESHOLD) & (dataset['cluster'] == -1))[0], 'cluster'] = cluster_id
            
    cluster_info = dataset['cluster'].value_counts().reset_index(drop=False)
    reset_idx = cluster_info.loc[cluster_info['cluster'] < MIN_NEIGHBOR_N, 'index'].tolist()
    dataset.loc[dataset['cluster'].isin(reset_idx), 'cluster'] = -1
    
    cluster_mapping = {x: i for i, x in enumerate(np.unique(dataset['cluster']))}
    dataset['cluster_idx'] = dataset['cluster'].apply(lambda x: cluster_mapping[x])
    
    if RETURN_ALL_COLS:
        dataset.to_excel(os.path.join(INPUT_DIR, args.output_file))
    elif TOPIC_COL and hasattr(dataset, TOPIC_COL):
        dataset[[RAW_TEXT_COL, TEXT_COL, TOPIC_COL, 'cluster_idx']].to_excel(os.path.join(INPUT_DIR, args.output_file))
    else:
        dataset[[RAW_TEXT_COL, TEXT_COL, 'cluster_idx']].to_excel(os.path.join(INPUT_DIR, args.output_file))
    print('Success')