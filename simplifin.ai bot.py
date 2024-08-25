
import streamlit as st
import requests
from openai import OpenAI

# Pass the API key when initializing the client
client = OpenAI(
    api_key="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")
rasa_url = "https://96bc-35-154-194-75.ngrok-free.app/webhooks/rest/webhook"

st.title("SimpliFin.ai Bot")
# Function to send a message to Rasa and get the response
def rasa_chat(question):
    custom_input = {
        'sender': 'user',  # Identifier for the user (can be any string)
        'message': f'{question}'  # Your custom input
    }

    response = requests.post(rasa_url, json=custom_input)

    if response.status_code == 200:
        response_json = response.json()
        for message in response_json:
            ans = f"{message['text']}"
        output = f"Your task is to answer the question from the data given, if answer is not found in data then give answer from your side. data:- {ans} question:- {question} "
        return output
    else:
        st.error(f"Error: {response.status_code}")
        return None


# Store the conversation history
if "history" not in st.session_state:
    st.session_state.history = []
if "rasa_history" not in st.session_state:
    st.session_state.rasa_history = []


# Function to handle the chat and update the UI
def send_message():
    question = st.session_state.user_input
    if question:
        # Add user's question to history
        st.session_state.history.append(f"You: {question}")

        rasa_out = rasa_chat(question)
        st.session_state.rasa_history.append(rasa_out)

        # Prepare question for OpenAI completion
        formatted_question = f"Your task is to answer the question from the data given to my user i always provide you data, if answer is not found in data, then give answer from your side. and no need to inform user The data provided does not contain information about, Only gives answer, please refer to the history first. question:- {st.session_state.history[-5:]} {question} , data:- {st.session_state.rasa_history[-5:]} {rasa_out} "

        # Get response from OpenAI
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": formatted_question}],
            stream=True,
        )

        answer = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                answer += f"{chunk.choices[0].delta.content}"

        # Add bot's response to history
        st.session_state.history.append(f"Bot: {answer}")
        st.session_state.user_input = ""  # Clear the input box


# Display the chat history
for i in range(len(st.session_state.history)):
    st.write(st.session_state.history[i])

# Input box for the user
st.text_input("You: ", key="user_input", on_change=send_message)


