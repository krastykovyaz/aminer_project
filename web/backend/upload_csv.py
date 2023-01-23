from glob import glob
import pandas as pd
import psycopg2 as postgres
from sqlalchemy import create_engine

engine = create_engine(
    'postgresql+psycopg2://aminer:team13best@aminer_postgres_db/aminer_db')

datasets_folder = './data'

# authors
# for chunk in pd.read_csv(f'{datasets_folder}/sample_authors.csv', sep='\t', encoding='utf-8', chunksize=10000):
#     chunk.to_sql('authors', engine, if_exists='append', index=False)

# venues
# for chunk in pd.read_csv(f'{datasets_folder}/sample_venues.csv', sep='\t', encoding='utf-8', chunksize=10000):
#     chunk.to_sql('venues', engine, if_exists='append', index=False)

# papers
# for chunk in pd.read_csv(f'{datasets_folder}/sample_papers.csv', sep='\t', encoding='utf-8', chunksize=10000):
#     chunk.to_sql('papers', engine, if_exists='append', index=False)

# author_paper
for chunk in pd.read_csv(f'{datasets_folder}/sample_author_paper.csv', sep='\t', encoding='utf-8', chunksize=10000):
    chunk.to_sql('author_paper', engine, if_exists='append', index=False)

# papers_refs
# for chunk in pd.read_csv(f'{datasets_folder}/sample_papers_refs.csv', sep='\t', encoding='utf-8', chunksize=10000):
#     chunk.to_sql('papers_refs', engine, if_exists='append', index=False)

# tags
# for chunk in pd.read_csv(f'{datasets_folder}/sample_tags.csv', sep='\t', encoding='utf-8', chunksize=10000):
#     chunk.to_sql('tags', engine, if_exists='append', index=False)
    
# papers_tags
# for chunk in pd.read_csv(f'{datasets_folder}/sample_papers_tags.csv', sep='\t', encoding='utf-8', chunksize=10000):
#     chunk.to_sql('papers_tags', engine, if_exists='append', index=False)

# user
# for chunk in pd.read_csv(f'{datasets_folder}/sample_users.csv', sep='\t', encoding='utf-8', chunksize=10000):
#     chunk.to_sql('user', engine, if_exists='append', index=False)
