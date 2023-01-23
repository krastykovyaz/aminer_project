import streamlit as st
import requests
from pandas import json_normalize
from json.decoder import JSONDecodeError

from authenticate.authenticate import Authenticate

BACKEND_URL = "http://172.17.0.1:5000"


def login_form(authenticator):
    authenticator.login("Login", "main")

    if st.session_state["authentication_status"] == "wrong_credentials":
        st.error("Username/password is incorrect")
    elif st.session_state["authentication_status"] == "registered":
        st.warning("Please enter your username and password")
    elif st.session_state["authentication_status"] == "logged_in":
        st.title("Aminer Project")
        nav = st.sidebar.radio("Navigation", ["Papers", "Authors"])

        if nav == "Papers":
            st.header("Papers")
        elif nav == "Authors":
            st.header("Authors")

        authenticator.logout("Logout", "sidebar")


def show_papers(papers):
    st.dataframe(json_normalize(papers)[['title', 'year']])


def main():
    authenticator = Authenticate("aminer_project", "abcdef", 30, test_mode=False)
    st.header("Welcome to Aminer Project!")

    def main_page():
        st.markdown("# Main page 🎈")
        st.sidebar.markdown("# Main page 🎈")
        authenticator.logout('Logout', 'sidebar')

    def search_page_papers_by_authors():
        st.markdown("# Search Papers By Author ❄️")
        st.sidebar.markdown("# Search Papers ❄️")
        
        author_name = st.text_input('Author name')
        if author_name:
            try:
                papers_by_author_name = requests.get(
                    f'{BACKEND_URL}/get_paper_by_author_name/{author_name}').json()
                show_papers(papers_by_author_name)
            except (JSONDecodeError, KeyError):
                st.write("Not found")
            
    def search_page_papers_by_year():
        st.markdown("# Search Papers By Year ❄️")
        st.sidebar.markdown("# Search Papers ❄️")
        
        year = st.text_input('Year')
        if year:
            try:
                papers_by_year = requests.get(
                    f'{BACKEND_URL}/get_paper_by_year/{year}').json()
                show_papers(papers_by_year)
            except (JSONDecodeError, KeyError):
                st.write("Not found")
            
    def search_page_papers_by_magazine():
        st.markdown("# Search Papers By Magazine ❄️")
        st.sidebar.markdown("# Search Papers ❄️")
        
        magazine = st.text_input('Magazine')
        if magazine:
            try:
                papers_by_magazine = requests.get(
                    f'{BACKEND_URL}/get_paper_by_vanue_raw/{magazine}').json()
                show_papers(papers_by_magazine)
            except (JSONDecodeError, KeyError):
                st.write("Not found")
                
    def search_page_papers_by_tag():
        st.markdown("# Search Papers By Tag ❄️")
        st.sidebar.markdown("# Search Papers ❄️")
        
        tag = st.text_input('Tag')
        if tag:
            try:
                papers_by_tag = requests.get(
                    f'{BACKEND_URL}/get_papers_by_tag/{tag}').json()
                show_papers(papers_by_tag)
            except JSONDecodeError:
                st.write("Not found")
                
    def top_authors_by_tag():
        st.markdown("# Top Authors By Tag ❄️")
        st.sidebar.markdown("# Top Authors ❄️")
        
        tag = st.text_input('Tag')
        if tag:
            try:
                authors_by_tag = requests.get(
                    f'{BACKEND_URL}/get_top_authors_by_tag/{tag}').json()
                st.dataframe(json_normalize(authors_by_tag))
            except JSONDecodeError:
                st.write("Not found")
                
    def recommmend_collaborators_by_author():
        st.markdown("# Recommend Collaborators ❄️")
        st.sidebar.markdown("# Recommend Page ❄️")
        
        author_name = st.text_input('Author name')
        if author_name:
            try:
                collaborators_by_author_name = requests.get(
                    f'{BACKEND_URL}/recommmend_collaborators_by_author_name/{author_name}').json()
                st.dataframe(json_normalize(collaborators_by_author_name)["name"])
            except (JSONDecodeError, KeyError):
                st.write("Not found")
                
    def recommmend_papers_by_author_name():
        st.markdown("# Recommend Papers ❄️")
        st.sidebar.markdown("# Recommend Page ❄️")
        
        author_name = st.text_input('Author name')
        if author_name:
            try:
                papers_by_author_name = requests.get(
                    f'{BACKEND_URL}/recommmend_papers_by_author_name/{author_name}').json()
                show_papers(papers_by_author_name)
            except (JSONDecodeError, KeyError):
                st.write("Not found")
        

    page_names_to_funcs = {
        "Main Page": main_page,
        "Search Papers By Author": search_page_papers_by_authors,
        "Search Papers By Year": search_page_papers_by_year,
        "Search Papers By Magazine": search_page_papers_by_magazine,
        "Search Papers By Tag" : search_page_papers_by_tag,
        "Top Authors By Tag": top_authors_by_tag,
        "Recommend Collaborator" : recommmend_collaborators_by_author,
        "Recommend Papers" : recommmend_papers_by_author_name,
    }

    if st.session_state['authentication_status'] == 'logged_in':
        selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
        page_names_to_funcs[selected_page]()
    elif st.session_state['authentication_status'] is None or st.session_state['authentication_status'] == "registered":
        authenticator.login("Login", "main")
        
        # TODO: enable this form after fix register fields
        # register = st.button("Register")

        # if register:
            # if authenticator.register_user('Register user'):
                # st.success('User registered successfully')
                # st.session_state['authentication_status'] = 'registered'


if __name__ == "__main__":
    main()
