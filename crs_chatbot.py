# main.py
import openai
from openai_config import API_KEY, WEBSITE_CONTENT
from autogen import AssistantAgent, GroupChatManager, UserProxyAgent, config_list_from_json
from autogen.agentchat import GroupChat
import streamlit as st
import re
import autogen
import panel as pn
import json

# Set OpenAI API key
openai.api_key = API_KEY
my_variable = ""

config_list = [
    {
        "api_base": "http://localhost:1234/v1",
        "api_type": "open_ai",
        "api_key": "sk-",
    }
]

config_list = config_list_from_json(
    env_or_file="OAI_CONFIG_LIST.json",
    file_location=".",
)

llm_config = {"config_list": config_list, "seed": 42, "request_timeout": 600,
              "temperature": 0,}

def extract_links_and_images(text):
    # Extract URLs from the text using a simple regex
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    return urls
def is_question_about_website(user_input):
    # Add keywords that indicate a question related to the website
    website_keywords = ["features", "information", "details", "content", "product"]

    # Check if any of the keywords are present in the user's input
    return any(keyword in user_input.lower() for keyword in website_keywords)

admin = UserProxyAgent(
    name="admin",
    human_input_mode="ALWAYS",
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
                      Otherwise, reply CONTINUE, or the reason why the task is not solved yet.""",
    llm_config=llm_config,
    code_execution_config=False,
)

Marketing = AssistantAgent(
    name="Marketing",
    llm_config=llm_config,
    system_message="Marketing. Develop and implement effective strategies to promote and market our SaaS product based on market trends and customer needs."
)

Sales = AssistantAgent(
    name="Sales",
    llm_config=llm_config,
    system_message="Sales. Implement approved marketing and sales strategies to attract customers and drive revenue for our SaaS solution."
)

Planner = AssistantAgent(
    name="Planner",
    llm_config=llm_config,
    system_message="""Planner. Develop comprehensive plans for marketing, sales, and product development. Iterate based on feedback from admin, critic, and teams involved. Clearly outline tasks for Marketing, Sales, Product, and address feedback effectively."""
)

Product = AssistantAgent(
    name="Product",
    llm_config=llm_config,
    system_message="Product. Ensure the accurate implementation of specifications for the SaaS-based product, adhering to approved plans and meeting customer expectations."
)

Builder = AssistantAgent(
    name="Builder",
    llm_config=llm_config,
    system_message="""Builder. Focus on the technical aspects of the SaaS product. Collaborate with the Product team to ensure the implementation aligns with technical specifications. Provide insights into the development process, technology stack, and address technical challenges."""
)

critic = AssistantAgent(
    name="critic",
    system_message="""critic. Thoroughly review plans and claims from other agents. Offer constructive feedback to enhance the quality of marketing, sales, product, and technical strategies. Ensure plans include verifiable information and reliable sources.""",
    llm_config=llm_config,
)
groupchat = GroupChat(
    agents=[Sales,Marketing,Product,Planner,critic],
    messages=[],
    max_round=500,
)
manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)
avatar = {admin.name:"👨‍💼", Marketing.name:"👩‍💻", Sales.name:"👩‍🔬", Planner.name:"🗓", Product.name:"🛠", critic.name:'📝'}

def ask_question(prompt):
    # Make an API call to OpenAI GPT-3
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )

    print(response)  # Print the raw response for debugging

    answer = response.choices[0].text.strip()
    answer = answer.lstrip('\n')
    # answer = response

    # answer = re.sub(r'/\w+ ', '/', answer)
    # Extract links and images from the answer
    media_urls = extract_links_and_images(answer)

    if media_urls:
        answer += "\n" + "\n".join([f'<a href="{url}" target="_blank">{url}</a>' for url in media_urls])

    return answer

def main():

# Streamlit CSS
    st.markdown(
    """
    <style>
        .chat-container {
            max-width: 400px;
            max-hight: 300px;
            margin: 50px auto;
            border: 1px solid #ccc;
            border-radius: 5px;
            overflow: hidden;
            background-color: #f4f4f4;
            flex-grow: 1;
        }

        .chat-header {
            background-color: #c41212;
            color: #fff;
            padding: 10px;
            text-align: center;
            font-size: 20px;
            font-weight: 10px;
        }

        .chat-messages {
            max-height: 300px;
            overflow-y: auto;
            padding: 10px;
        }

        .message {
            margin-bottom: 10px;
        }

        .message.sender {
            text-align: right;
        }

        .message.sender .message-body {
            background-color: #c41212;
            color: #fff;
            border-radius: 10px;
            padding: 8px 12px;
            display: inline-block;
        }

        .message.receiver .message-body {
            background-color: #ddd;
            border-radius: 10px;
            padding: 8px 12px;
            display: inline-block;
        }

        .message-body {
            max-width: 70%;
            word-wrap: break-word;
        }

        .input-container {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            position: fixed;
            bottom: 0;
            left: 30%;
            width: 40%;
            padding: 10px;
            background-color: #eee;
            border-top: 1px solid #ccc;
        }

        .input-container input {
            width: 80%;
            padding: 8px;
            box-sizing: border-box;
            border: none;
            border-radius: 5px;
        }

        .input-container button {
            width: 18%;
            padding: 8px;
            box-sizing: border-box;
            border: none;
            border-radius: 5px;
            background-color: #c41212;
            color: #fff;
            cursor: pointer;
        }
    </style>
    """,
    unsafe_allow_html=True,
    )

    st.markdown(
    """
    <div class="chat-header">CSR Virtual Assistant</div>
        <div class="chat-messages">
    """,
    unsafe_allow_html=True,
    )

    user_input = st.chat_input("Say something")

    # Initialize session state to store the conversation history
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    if user_input:
        # Concatenate user's input with the previous conversation
        prompt = "\n".join([interaction['text'] for interaction in st.session_state.conversation_history])
        prompt += f"\nUser: {user_input}\nWebsite Content: {WEBSITE_CONTENT}"

        # Ask a question using OpenAI GPT-3
        answer = ask_question(prompt)

        # Store the conversation history
        st.session_state.conversation_history.append({"speaker": "You", "text": user_input})
        st.session_state.conversation_history.append({"speaker": "Assistant", "text": answer})
        
        # Clear user_input after processing by setting it to an empty string
        user_input = ""


    # Display the conversation messages
    for interaction in st.session_state.conversation_history:
        if interaction['speaker'] == "You":
            st.markdown(f'<div class="message sender"><div class="message-body">You: {interaction["text"]}</div></div>', unsafe_allow_html=True)
        elif interaction['speaker'] == "Assistant":
            st.markdown(f'<div class="message receiver"><div class="message-body">Assistant: {interaction["text"]}</div></div>', unsafe_allow_html=True)
    
    st.markdown(
        """
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
