from openai import OpenAI


import os
api_key: str = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

from datetime import datetime, timedelta
import random
import time
import streamlit as st
import pandas as pd


from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS



def find_similarity(representative, query, type, k=8):
    examples = ''
    try:
        if type == 'nonmember_respond':
            print("------ Non Member Respond Rag 1 --------\n")
            k=4
            full_file = 'Rag_new_examples/nonmember_respond.csv'
            col1 = 'Rag_new_examples/nonmember_respond_col1.csv'

        elif type == 'member_respond':
            print("------ Member Respond Rag 2 --------\n")
           
            k=4
            full_file = 'Rag_new_examples/member_respond.csv'
            col1 = 'Rag_new_examples/member_respond_col1.csv'
            
        elif type == 'nonmember_signup':
            print("------Non Member Signup Rag 3--------\n")
            full_file = 'Rag_new_examples/nonmember_signup.csv'
            col1 = 'Rag_new_examples/nonmember_signup_col1.csv'
                

        elif type == 'member_upgrade':
            print("------Member Upgrade Rag 4--------\n")
            full_file = 'Rag_new_examples/nonmember_upgrade.csv'
            col1 = 'Rag_new_examples/nonmember_upgrade_col1.csv'

            
        loader = CSVLoader(file_path=col1)
        data = loader.load()
        embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        db = FAISS.from_documents(data, embeddings)  

        docs = db.similarity_search(query, k)
        df = pd.read_csv(full_file)
        for index, doc in enumerate(docs):
            input_text = doc.page_content[14:]
            if len(input_text) > 0:    
                try:
                    mask = df['User Message'] == input_text 
                    output = df.loc[mask, 'Assistant Message'].iloc[0]
                except IndexError:
                    print('no similarity found')

                try:
                    if type in ['nonmember_respond','member_respond']:
                        examples += f'{output} \n\n'
                    else:    
                        examples += f'Example {index +1 }: \n\nLead Email: {input_text} \n\n {representative} Response: {output} \n\n'
                except:
                    continue
        return examples
    except Exception as e:
        print("error in find_examples", e)    
        return examples








#generate openai response; returns messages with openai response
def ideator(messages, lead_dict_info, bot_used):
    print('message length: ' + str(len(messages)))
    prompt = messages[0]['content']
    messages = messages[1:]
    new_message = messages[-1]['content']

    #perform similarity search
    examples = find_similarity(lead_dict_info.get('agent_name'), new_message, bot_used, k=4)
    print('examples: ' ,examples)
    st.sidebar.write(examples)
    examples = examples.format(**lead_dict_info)
    prompt = prompt + examples
    print('inbound message: ' + str(messages[-1]))
    print('prompt' + prompt)
    print('\n\n')
    prompt = {'role': 'system', 'content': prompt}
    messages.insert(0,prompt)
    
    for i in range(5):
        try:
            response = client.chat.completions.create(model = 'gpt-4o', messages = messages,  max_tokens = 500, temperature = 0)
            response =  response.choices[0].message.content
            section ={ "role": "assistant", "content": response }
            messages.append(section)
            return messages
        except Exception as e: 
            error_message = f"Attempt {i + 1} failed: {e}"
            print(error_message)
            if i < 4:  # we don't want to wait after the last try
                time.sleep(5)  # wait for 5 seconds before the next attempt
    

def get_initial_message(campaign, prior_nmqrs, quote_lead_goal_mode):
    initial_message =None
    if campaign == 'Received NMQR' and prior_nmqrs in [None, '0', 0] and quote_lead_goal_mode != 'Needs Response' :
        print(f"1 : {campaign} == Received NMQR' and prior_nmqrs == 0 and quote_lead_goal_mode == No need response")
        initial_message = '''Hey {lead_first_name}<br><br>I noticed that you recently received your very first quote request from a planner {reseller_org_name} on Reposite - congrats!<br>Are you the right person at your company that handles group reservations?<br><br>Cheers,<br>{representative}'''
    elif campaign == 'Received NMQR' and prior_nmqrs in [None, '0', 0] and quote_lead_goal_mode == 'Needs Response' : 
        print(f"2 :  {campaign} == Received NMQR' and prior_nmqrs == 0 and quote_lead_goal_mode == need response") 
        initial_message = '''Hey {lead_first_name}<br><br>I noticed that you recently received your very first quote request from a planner {reseller_org_name} on Reposite - congrats! It appears that they have a tight deadline for response though.<br>If you have availability on {trip_start_date} could you sign up and reply to them today? Here's the link if you lost the initial request {nmqrurl}<br><br>Cheers,<br>{representative}'''
    elif campaign == 'Received NMQR' and prior_nmqrs not in [None, '0', 0] and quote_lead_goal_mode != 'Needs Response' :
        print(f"3 :  {campaign} == Received NMQR' and prior_nmqrs > 0 and quote_lead_goal_mode == no need response") 
        initial_message = ''' Hey {lead_first_name}<br><br>I saw you got another group reservation request through Reposite from a new planner!<br>Are you the right person at your company that handles group reservations?<br><br>Cheers,<br>{representative}'''
    elif campaign == 'Received NMQR' and prior_nmqrs not in [None, '0', 0] and quote_lead_goal_mode == 'Needs Response' :  
        print(f"4 :  {campaign} == Received NMQR' and prior_nmqrs > 0 and quote_lead_goal_mode ==  need response") 
        initial_message = '''Hey {lead_first_name}<br><br>I noticed that you recently received a quote request from a travel planner on Reposite.<br>It appears our travel planner is working on a tight schedule and need a reply today. Here's the link {nmqrurl} to view and reply.<br> Are you the right person at your company that handles group reservations? <br><br>Cheers,<br> {representative}''' 
    elif campaign == 'New QR' and quote_lead_goal_mode != 'Needs Response' :
        print(f"5 :  {campaign} == New QR' and quote_lead_goal_mode == no need response") 
        initial_message = '''Hey {lead_first_name}<br><br>I saw you got another group reservation request through Reposite from a new planner!<br> Are you the right person at your company that handles group reservations?<br><br> Cheers,<br>{representative}'''
    elif campaign == 'New QR' and quote_lead_goal_mode == 'Needs Response' :  
        print(f"6 :  {campaign} == New QR' and quote_lead_goal_mode == need response") 
        initial_message = '''Hey {lead_first_name}<br><br>I noticed that you recently received a quote request from a travel planner on Reposite.<br>It appears our travel planner is working on a tight schedule and need a reply today. Here's the link {nmqrurl} to view and reply.<br>Are you the right person at your company that handles group reservations?<br><br>Cheers,<br>{representative}'''
    elif campaign == 'Token Change' :  
        print(f"7 :  {campaign} == Token Change") 
        initial_message = '''Hey {lead_first_name}<br><br>I saw that you just used tokens to discover new group planners. It's great to see you taking active steps to expand your connections!<br>Are there certain types of planners that you're targeting (corporate, student groups, international groups, luxury, etc.)?<br><br> Cheers,<br>{representative}''' 
    elif campaign == 'Quote Hotlist' :  
        print(f"8 :  {campaign} == Quote Hotlist") 
        initial_message = '''Hey {lead_first_name}<br><br>I noticed that your conversation (with a planner on Reposite) is off to a good start - congrats (though I don't want to jinx it)!<br>Are you open to receiving more quotes and group leads from other planners?<br><br> Cheers,<br>{representative}'''     
    elif campaign == 'Booking Received' :  
        print(f"9 :  {campaign} == Booking Received") 
        initial_message = ''' Hey {lead_first_name}<br><br>I noticed that your conversation (with a planner on Reposite) is off to a good start - congrats (though I don't want to jinx it)!<br>Are you open to receiving more quotes and group leads from other planners? <br><br> Cheers,<br>{representative}'''    
    elif campaign == 'Newly Onboarded': 
        print(f"10:  {campaign} == Newly Onboarded'") 
        initial_message = '''Hey {lead_first_name}<br><br>I saw you just set up an account for {supplier_name} on Reposite! Congrats on being invited by {reseller_org_name}.<br> So we can help tailor future leads for you: what's your ideal type of group business (corporate, student groups, international groups, luxury, etc.)?<br><br> Cheers,<br>{representative}'''       
    return initial_message

