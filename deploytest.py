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
assistant_id = st.secrets("ASSISTANT_ID")
 
def assistantAPI(prompt):
    # Create a thread
    thread = client.beta.threads.create(
         messages=[
            {
            "role": "user",
            "content": prompt
            }
        ]
    )

    # Run the thread and poll for the result
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )
 
    status = run.status
 
    while status not in ["completed", "cancelled", "expired", "failed"]:
        time.sleep(5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id,run_id=run.id)
        print("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60), int((time.time() - start_time) % 60)))
        status = run.status
        #print(f'Status: {status}')
 
 
    messages = client.beta.threads.messages.list(
    thread_id=thread.id
    )
 
    data = json.loads(messages.model_dump_json(indent=2))
    print(data)
 
    # loop through a JSON array of messages
    for i in range(len(data['data'][0]['content'])):
 
        #check to see if ['content'][i] contains 'text'
        if 'text' in data['data'][0]['content'][i]:
            response = data['data'][0]['content'][i]['text']['value']
            #print(response)
 
    return response
 
 
# add streamlit title
st.title("HKN In Store Assistant Copilot")
# Load the logo image
logo_path = "heinekenlogo.png"  # Update this with the correct path to your logo

st.sidebar.empty()  # Create an empty space element
# Add logo to the sidebar with some space above it
st.sidebar.image(logo_path, use_column_width=True)
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