import requests
import json

class GLM:
    def __init__(self):
        with open('D:\holk\CyberFriend\plugins\cyber_friend\prompt.txt', encoding='utf-8') as f:
            self.prompt = f.read()

    def call(self, records):
        # Define the URL and the payload for the POST request
        url = "http://100.87.223.81:9021/v1/chat/completions"
        data = {
            "model": "chatglm3-6b",
            "messages": [
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": str(records)}
            ],
            "stream": False,
            "max_tokens": 100,
            "temperature": 0.8,
            "top_p": 0.8
        }
        # Make the POST request
        response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response to extract the 'content'
            response_json = response.json()
            content = response_json.get('choices', [{}])[0].get('message', {}).get('content', 'No content found')
        else:
            content = f"Failed to fetch the story. Error code: {response.status_code}"
        return str(content)

if __name__ == "__main__":
    glm = GLM()
    print(type(glm.call('你好')))