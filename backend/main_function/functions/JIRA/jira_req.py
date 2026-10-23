import streamlit as st
import requests
import json


def get_jira_power_cons(API_KEY: str, model_name:str ):
    # 1. Use your Jira token for authorization
    headers = {
        "Accept" : "*/*",
        "Authorization": f"Bearer {API_KEY}",
        #"Referer": "http://collab.lge.com/main/pages/viewpage.action?pageId=2053155392&spaceKey=~weapon.ahn&title=PC03%2BDownload%2BTV%2BEnergy%2BIssues"
    }

    # 2. Target the Jira server with the correct /issue/ context path
    url_jira = r"http://jira.lge.com/issue/rest/api/2/search"
    url_jira_energy_issue = r"http://collab.lge.com/main/rest/jiraanywhere/1.0/jira/renderTable"
    # (The rest of your headers, params, and requests.post code remains exactly the same)

    # 3. Use the standard Jira API payload format instead of wikiMarkup
    params_jira = {
        "jql": 'project = TVPDFT AND labels = GLZ AND labels = webOS26 AND text ~ "*" ORDER BY createdDate DESC',
        "maxResults": 1000
    }

    params_jira_all = {"wikiMarkup":"<ac:structured-macro ac:name=\"jira\" ac:schema-version=\"1\"><ac:parameter ac:name=\"server\">NEXT JIRA</ac:parameter><ac:parameter ac:name=\"columns\">key,summary,type,created,updated,assignee,reporter,priority,status,resolution,labels</ac:parameter><ac:parameter ac:name=\"maximumIssues\">1000</ac:parameter><ac:parameter ac:name=\": = | TOKEN_TYPE | = :\">BLOCK</ac:parameter><ac:parameter ac:name=\"jqlQuery\">project = TVPDFT AND labels = GLZ AND labels = webOS27 ORDER BY createdDate DESC</ac:parameter></ac:structured-macro>","clearCache":"true"}

    params_jira_standard = {
        "jql": f"project = TVPDFT AND labels = GLZ AND labels = webOS27 AND text ~ '{model_name}' ORDER BY createdDate DESC",
        "maxResults": 1000,
    }

    # 4. Send the request
    response_check_jira = requests.post(url_jira, headers=headers, json=params_jira_standard)
    response_json = response_check_jira.json()

    #st.write(f"Status Code: {response_check_jira.status_code}")
    #st.json(response_check_jira.json())

    return response_json 