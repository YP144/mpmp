
import requests
import json

jira_key = "ODA3Mzc0ODAwMTY1OlHLm3Hs4YgvWCnHbHahhbNr5O2D"

def save_response_to_json(response, filename="output_all.json"):
    """
    Checks the response status and saves the data to a formatted JSON file if successful.
    """
    if response.status_code == 200:
        try:
            data = response.json()
            print(json.dumps(data, indent=4))
            
            with open(filename, "w", encoding="utf-8") as file:
                # ensure_ascii=False helps properly format non-English characters
                json.dump(data, file, indent=4, ensure_ascii=False)
                
            print(f"Data successfully saved to {filename}")
            
        except json.JSONDecodeError:
            print("Error: The response returned a 200 status, but the content is not valid JSON.")
    else:
        print(f"Error {response.status_code}: {response.text}")

# 1. Use your Jira token for authorization
headers = {
    "Accept" : "application/json",
    "Authorization": f"Bearer {jira_key}" 
}

# 2. Target the Jira server with the correct /issue/ context path
url_jira = r"http://jira.lge.com/issue/rest/api/2/search"

# (The rest of your headers, params, and requests.post code remains exactly the same)

# 3. Use the standard Jira API payload format instead of wikiMarkup
params_jira = {
    "jql": 'project = TVPDFT AND labels = GLZ AND labels = webOS26 AND text ~ "*" ORDER BY createdDate DESC',
    "maxResults": 1000
}

# 4. Send the request
response = requests.post(url_jira, headers=headers, json=params_jira)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=4))
    
    save_response_to_json(response, "my_custom_output.json")
else:
    print("Error:", response.text)