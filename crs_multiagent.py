
from autogen import AssistantAgent, GroupChatManager, UserProxyAgent, config_list_from_json
from autogen.agentchat import GroupChat
import spacy
import autogen
import panel as pn
import json
import os

config_list = [
    {
        "model": "gpt-3.5-turbo-0613",
        "api_key": os.getenv("OPENAI_API_KEY")
    }
]

# config_list = config_list_from_json(
#     env_or_file="OAI_CONFIG_LIST.json",
#     file_location=".",
# )

llm_config = {"config_list": config_list, "seed": 42, "timeout": 600,
              "temperature": 0,}

admin = UserProxyAgent(
    name="admin",
    human_input_mode="ALWAYS",
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
                      Otherwise, reply CONTINUE, or the reason why the task is not solved yet.""",
    llm_config=llm_config,
    code_execution_config=False,
)

DesignConsultants = AssistantAgent(
    name="DesignConsultants",
    system_message="""
Design Consultants. Building upon the user input, the Design Consultant takes on the role of providing aesthetic guidance and design support. 
Collaborating closely with the customer, the design consultant delves into the specifics of the design vision. 
you expert advice on selecting bricks that align with the desired aesthetic, considering considerations such as color, 
texture, and patterns. You can recommend multiple options to the customer.
You play a crucial role in creating a cohesive and visually appealing brick design tailored to the project. You have to give the available bricks option and the most suitable brick for the customer's needs. Need to give basic details about that brick.
You only need to answer based on the https://www.pghbricks.com.au/ 
      website content.You should not mention the brick not available on the PGH website. And you act as Design Consultant at PGH Bricks""",
    llm_config=llm_config,
)

TechnicalExpert = AssistantAgent(
    name="TechnicalExpert",
    llm_config=llm_config,
    system_message="""Once the design is finalized, your role is to evaluate the structural requirements of the project. 
    your responsibilities include analyzing the design to understand the project's structural needs. You have to think as a technical expert and give feedback and input if the design consultant recommends brick is suitable or not.
      and need to tell you about the technical side. If DesignConsultants recommends multiple you have to give each of the selections feedback.
    You provide recommendations that not only meet building codes and standards but also contribute to 
    the overall stability and safety of the construction project.
      You address technical concerns and ensure that the chosen bricks align with the structural requirements. Need to check the technical specification and mentiond in the replay.
      Need to give a detailed answer according to your role.
      You only need to answer based on the https://www.pghbricks.com.au/ 
      website content.You should not mention the brick not available on the PGH website. And you act as a Technical Expert at PGH Bricks""",)


QualityControlSpecialist = AssistantAgent(
    name="QualityControlSpecialist",
    system_message="""The Quality Control Specialist. Your role is to ensure the product quality. You verify that the selected bricks by DesignConsultants meet the company's stringent
      quality standards and specifications. Through detailed quality checks, 
    you have to report on the durability, strength, and longevity of the chosen bricks. Additionally, you provide comprehensive information on the quality assurance
      processes in place, instilling confidence in the customer regarding the selected materials. You need to give a detailed answer based on your role. You only need to answer based on the https://www.pghbricks.com.au/ 
      website content.You should not mention the brick not available on the PGH website. And you act as Quality Control Specialist at PGH Bricks""",
    llm_config=llm_config,
)

SalesRepresentatives = AssistantAgent(
    name="SalesRepresentatives",
    llm_config=llm_config,
    system_message="""
     Sales Representative, At the end of the consultation process for selecting bricks, you give the overall feedback to the customer based on the ideas of
       Design Consultants, Technical Expert, Quality Control Specialist.
       Mentioned the brick or bricks that are most suitable for the customer's needs if prices range can menton, add price details also. And include brick shape, color, overall look. 
       And you have to promote your company and recommend items to increase the 
       sales. You only need to answer based on the https://www.pghbricks.com.au/ 
      website content.You should not mention the brick not available on the PGH website.You act as a Sales Representative at PGH Bricks""",
)

groupchat = GroupChat(
    agents=[DesignConsultants,TechnicalExpert,QualityControlSpecialist,SalesRepresentatives],
    messages=[],
    max_round=10,
)
manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)
avatar = {admin.name:"👨‍💼", DesignConsultants.name:"👩‍🔬", TechnicalExpert.name:"🗓", QualityControlSpecialist.name:"🛠", SalesRepresentatives.name:"👩‍💻"}


nlp = spacy.load("en_core_web_sm")

stop_conversation = False

def contains_request_for_more_info(message):
    # Perform more sophisticated NLP-based analysis here
    doc = nlp(message)
    
    # Check for keywords indicating a request for more information
    keywords = ["need more information", "provide more details", "not enough information", "please provide", "How can I assist you"]
    for keyword in keywords:
        if keyword in message.lower():
            return True

    return False

def get_custom_agent_name(agent_name):
    # Customize the agent name as needed
    if agent_name == 'TechnicalExpert':
        return 'Technical Expert'
    elif agent_name == 'DesignConsultants':
        return 'Design Consultants'
    elif agent_name == 'QualityControlSpecialist':
        return 'Quality Control Specialist'
    elif agent_name == 'SalesRepresentatives':
        return 'Sales Representatives'
    else:
        return agent_name

def is_relevant_question(message):
    # Customize the keywords based on the expected content relevant to the duties
    relevant_keywords = ["brick","service","project","roof tiles", "construction", "aesthetic guidance", "structural requirements", "product quality", "sales", "color"]
    
    # Check if any of the relevant keywords are present in the message
    return any(keyword.lower() in message.lower() for keyword in relevant_keywords)


def is_not_relevant_anwser(message):
    # Customize the keywords based on the expected content relevant to the duties
    relevant_keywords = ["is not relevant","I dont have anwser"," I am not equipped to", "I'm sorry, but as a "]
    
    # Check if any of the relevant keywords are present in the message
    return any(keyword.lower() in message.lower() for keyword in relevant_keywords)

def print_messages(recipient, messages, sender, config):
    global stop_conversation
    try:
        _avatar = avatar.get(messages[-1].get('name', 'admin'))
        _user = messages[-1].get('name', 'Assistant')
        _message = messages[-1].get('content', '')

        # Stop the conversation after Sales Representative replies
        if _user == 'SalesRepresentatives':
            stop_conversation = True  
            chat_interface.send(_message, 'PGH Bricks', avatar=_avatar, respond=False)
            return stop_conversation, None

        # Check if the DesignConsultants agent has requested more information
        if _user != 'admin' and contains_request_for_more_info(_message):
            chat_interface.send(_message, _user, avatar=_avatar, respond=False)
            stop_conversation = True  # Stop the conversation
        
        elif _user == 'admin':
            stop_conversation = False
        # Continue the conversation if the condition is not met
            
        # Check if the message is off-topic
        elif not stop_conversation and not is_relevant_question(_message):
            # Respond to irrelevant questions
            irrelevant_response = "I'm sorry, but your question is not relevant to the services provided by our company. If you have questions about bricks, construction, or related topics, feel free to ask."
            chat_interface.send(irrelevant_response, 'PGH Bricks', avatar=_avatar, respond=False)
            stop_conversation = True  # Stop the conversation for irrelevant questions
        
        elif not stop_conversation and is_not_relevant_anwser(_message):
            # Respond to irrelevant questions
            irrelevant_response = "I'm sorry, but your question is not relevant to the services provided by our company. If you have questions about bricks, construction, or related topics, feel free to ask."
            chat_interface.send(irrelevant_response, 'PGH Bricks', avatar=_avatar, respond=False)
            stop_conversation = True  # Stop the conversation for irrelevant questions

        # Continue the conversation if the condition is not met
        elif not stop_conversation:
            custom_agent_name = get_custom_agent_name(_user)
            chat_interface.send(_message, custom_agent_name, avatar=_avatar, respond=False)

        return stop_conversation, None
    except Exception as e:
        print("An error occurred:", e)

def is_question(message):
    # Implement your logic to check if the message is a question
    # You can use NLP techniques, regex, or any other method
    # Here, a simple check is performed if the message ends with a question mark
    return message.strip().endswith('?')

admin.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
)


DesignConsultants.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
)

TechnicalExpert.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
)
QualityControlSpecialist.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
)

SalesRepresentatives.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
)


pn.extension(design="material")

def custom_renderer(value):
    return f'<span style="background-color: yellow;">{value}</span>'

def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    admin.initiate_chat(
    manager,
    message=contents
)
    

template = pn.template.BootstrapTemplate(title='AutoGen Chatbot')

chat_interface = pn.chat.ChatInterface(callback=callback, user="You", renderers=[custom_renderer])

template.main.append(chat_interface)

chat_interface.send("Hi Welcome to the PGH Brick Consulatation Platform", user="PGH Bricks", respond=False)

template.servable();

