import streamlit as st
from openai import AzureOpenAI
import time
from IPython.display import clear_output
import json
import os 
start_time = time.time()


client = AzureOpenAI(
    api_key= st.secrets["AZURE_OPENAI_KEY"],  
    api_version="2024-05-01-preview",
    azure_endpoint = "https://kh-gptmodeltest.openai.azure.com/"
    )
assistant_id = st.secrets["ASSISTANT_ID"]
 
# def assistantAPI(prompt):
#     # Create a thread
#     thread = client.beta.threads.create(
#          messages=[
#             {
#             "role": "user",
#             "content": prompt
#             }
#         ]
#     )

#     # Run the thread and poll for the result
#     run = client.beta.threads.runs.create_and_poll(
#         thread_id=thread.id,
#         assistant_id=assistant_id,
#     )
 
#     status = run.status
 
#     while status not in ["completed", "cancelled", "expired", "failed"]:
#         time.sleep(8)
#         run = client.beta.threads.runs.retrieve(thread_id=thread.id,run_id=run.id)
#         print("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60), int((time.time() - start_time) % 60)))
#         status = run.status
#         #print(f'Status: {status}')
 
 
#     messages = client.beta.threads.messages.list(
#     thread_id=thread.id
#     )
 
#     data = json.loads(messages.model_dump_json(indent=2))
#     print(data)
 
#     # loop through a JSON array of messages
#     for i in range(len(data['data'][0]['content'])):
 
#         #check to see if ['content'][i] contains 'text'
#         if 'text' in data['data'][0]['content'][i]:
#             response = data['data'][0]['content'][i]['text']['value']
#             #print(response)
 
#     return response
def assistantAPI(prompt):
    # Create a thread
    thread = client.beta.threads.create(
        messages=[{"role": "user", "content": prompt}]
    )

    # Start timing for elapsed time reporting
    start_time = time.time()

    # Run the thread and poll for the result
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

    # Poll until the run status is one of the terminal states
    status = run.status
    #while status not in ["completed", "cancelled", "expired", "failed"]
    while status in ['queued', 'in_progress', 'cancelling']:
        time.sleep(8)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        elapsed_time = time.time() - start_time
        print("Elapsed time: {} minutes {} seconds".format(int(elapsed_time // 60), int(elapsed_time % 60)))
        status = run.status

    # Retrieve messages from the thread
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    data = json.loads(messages.model_dump_json(indent=2))

    # Initialize a list to hold all responses
    responses = []

    # Loop through the messages to find all assistant responses
    for message in data['data']:
        if message['role'] == 'assistant' and 'content' in message and isinstance(message['content'], list):
            for content in message['content']:
                if 'text' in content:
                    # Prepend each response to the list
                    responses.insert(0, content['text']['value'])

    # Get the last two responses in correct order
    last_two_responses = responses[:2] if len(responses) >= 2 else responses

    # Join the last two responses into a single string
    full_response = "\n\n".join(last_two_responses) if last_two_responses else "No response found."

    # Return the complete response
    return full_response
 
 
# add streamlit title
st.title("HKN In Store Assistant Copilot")
# Load the logo image
#logo_path = "heinekenlogo.png"  # Update this with the correct path to your logo

st.sidebar.empty()  # Create an empty space element
# Add logo to the sidebar with some space above it
#st.sidebar.image(logo_path, use_column_width=True)
# Add a dropdown list (select box) to the sidebar
st.sidebar.title("Choose Brand")
brands = ["ALL","ABC", "Heineken", "Tiger","Anchor","Gold Crown"]
selected_brand = st.sidebar.selectbox("Brand:", brands)
 
# add a streamlit left hand navigation bar
st.sidebar.title("Upload File")
 
# Add a file upload control in the sidebar
uploaded_file = st.sidebar.file_uploader("Choose a file")
 
if "messages" not in st.session_state:
    st.session_state.messages = []
    #st.session_state.messages.append({"role": "system", "content": "HI, how may I help you?"})
if "model" not in st.session_state:
    st.session_state.model = "kh-gptmodel-4o"
       
# User input
if user_prompt := st.chat_input("Your prompt"):
    # Get response from assistant
    response = assistantAPI(user_prompt)
    # Store user message in session state
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    # Store assistant's response in session state
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display the chat history
for message in st.session_state.messages:
    role = "👤" if message["role"] == "user" else "🤖"
    st.markdown(f"**{role}**: {message['content']}")
