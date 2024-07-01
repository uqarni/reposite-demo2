import openai
import os
import re
import random
from datetime import datetime, timedelta
import random
import time

#similarity search
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import pandas as pd

from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

def find_txt_examples(query, k=8):
    loader = TextLoader("examples.txt")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    
    embeddings = OpenAIEmbeddings()

    db = FAISS.from_documents(docs, embeddings)
    docs = db.similarity_search(query, k=k)

    examples = ""
    for doc in docs:
       examples += '\n\n' + doc.page_content
    return examples


def find_examples(query, type, k=8):
    examples = ''
    try:
        if type == 'nonmember_respond':
            print("------Non Member Respond Rag 1--------\n")
            k=4
            full_file = 'Rag_new_examples/non-member-supplier-upgrade.csv'
            col1 = 'Rag_new_examples/non-member-supplier-upgrade-col1.csv'

        elif type == 'member_respond':
            print("------Member Respond Rag 2--------\n")
           
            k=4
            full_file = 'Rag_new_examples/member-supplier-upgrade.csv'
            col1 = 'Rag_new_examples/member-supplier-upgrade-col1.csv'
            
        elif type == 'nonmember_signup':
            print("------Non Member Signup Rag 3--------\n")
            full_file = 'Rag_new_examples/non-member-nmqr.csv'
            col1 = 'Rag_new_examples/non-member-nmqr-col1.csv'
                

        elif type == 'member_upgrade':
            print("------Member Upgrade Rag 4--------\n")
            full_file = 'Rag_new_examples/member-nmqr.csv'
            col1 = 'Rag_new_examples/member-nmqr-col1.csv'
            
        loader = CSVLoader(file_path=col1)
        data = loader.load()
        embeddings = OpenAIEmbeddings()
        db = FAISS.from_documents(data, embeddings)  

        docs = db.similarity_search(query, k)
        df = pd.read_csv(full_file)
        for index, doc in enumerate(docs):
            input_text = doc.page_content[14:]
            if len(input_text) > 0:    
                try:
                    # print(f"\n{index +1}", input_text)
                    mask = df['User Message'] == input_text 
                    output = df.loc[mask, 'Assistant Message'].iloc[0]
                    # print(">>>", output)
                except IndexError:
                    print('no similarity found')

                try:
                    if type in ['nonmember_respond','member_respond']:
                        examples += f'{output} \n\n'
                    else:    
                        # representative = 'Lee' if lee else 'Taylor'
                        examples += f'Example {index +1 }: \n\nLead Email: {input_text} \n\n Taylor Response: {output} \n\n'
                except:
                    continue
        return examples
    except Exception as e:
        print("error in find_examples", e)    
        return examples

  

def my_function(og, permuted):
    try:
        output = find_examples(permuted, k = 10)
        if og in output:
            return 'yes'
        else:
            return 'no'
    except:
        print('error')
        print('\n\n')
        return 'error'
    
# Read CSV
def find_in_examples_script():
    df = pd.read_csv('oct12comparison.csv')

    # Apply function to each row and store result in a new column
    df['Output'] = df.apply(lambda row: my_function(row['Assistant Reference Message'], row['Modified user message']), axis=1)

    # Write DataFrame back to CSV
    df.to_csv('oct12comparison_modified.csv', index=False)


















#generate openai response; returns messages with openai response
def ideator(messages, lead_dict_info, bot_used):
    print('message length: ' + str(len(messages)))
    prompt = messages[0]['content']
    messages = messages[1:]
    new_message = messages[-1]['content']

    #perform similarity search
    examples = find_examples(new_message, bot_used, k=4)
    print('examples: ' ,examples)
    examples = examples.format(**lead_dict_info)
    prompt = prompt + examples
    print('inbound message: ' + str(messages[-1]))
    print('prompt' + prompt)
    print('\n\n')
    prompt = {'role': 'system', 'content': prompt}
    messages.insert(0,prompt)
    
    for i in range(5):
      try:
        key = os.environ.get("OPENAI_API_KEY")
        openai.api_key = key
    
        result = openai.ChatCompletion.create(
          model="gpt-4o",
          messages= messages,
          max_tokens = 500,
          temperature = 0
        )
        response = result["choices"][0]["message"]["content"]
        # response = response.replace('\n','<br>')
        print('response:')
        print(response)
        print('\n\n')
        break
      except Exception as e: 
        error_message = f"Attempt {i + 1} failed: {e}"
        print(error_message)
        if i < 4:  # we don't want to wait after the last try
          time.sleep(5)  # wait for 5 seconds before the next attempt
  
    def split_sms(message):
        import re
  
        # Use regular expressions to split the string at ., !, or ? followed by a space or newline
        sentences = re.split('(?<=[.!?]) (?=\\S)|(?<=[.!?])\n', message.strip())
        # Strip leading and trailing whitespace from each sentence
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
  
        # Compute the cumulative length of all sentences
        cum_length = [0]
        for sentence in sentences:
            cum_length.append(cum_length[-1] + len(sentence))
      
            total_length = cum_length[-1]
  
        # Find the splitting point
        split_point = next(i for i, cum_len in enumerate(cum_length) if cum_len >= total_length / 2)
  
        # Split the sentences into two parts at the splitting point
        part1 = sentences[:split_point]
        part2 = sentences[split_point:]
  
        # Join the sentences in each part back into strings and exclude any part that is empty
        strings = []
        if part1:
            strings.append(" ".join(part1))
        if part2:
            strings.append(" ".join(part2))
      
        return strings

    split_response = [response]
    count = len(split_response)
    for section in split_response:
        section = {
           "role": "assistant", 
           "content": section
           }
        messages.append(section)

    return messages, count


def initial_text_info(selection = None):
    initials = {
       "campaign == 'Received NMQR' and prior_nmqrs == 0 and quote_lead_goal_mode != 'Needs Response' ": '''
            Hey {lead_first_name} -

            I noticed that you recently received your very first quote request from a planner {reseller_org_name} on Reposite - congrats!

            Are you the right person at your company that handles group reservations?

            Cheers,
            Lee
            ''',

        "campaign == 'Received NMQR' and prior_nmqrs == 0 and quote_lead_goal_mode == 'Needs Response' ": '''
            Hey {lead_first_name} -

            I noticed that you recently received your very first quote request from a planner {reseller_org_name} on Reposite - congrats! It appears that they have a tight deadline for response though. 

            If you have availability on {trip_start_date} could you sign up and reply to them today? Here's the link if you lost the initial request {nmqrurl}

            Cheers,
            Lee
            ''',

        "campaign == 'Received NMQR' and prior_nmqrs > 0 and quote_lead_goal_mode != 'Needs Response' ": '''
            Hey {lead_first_name} -

            I saw you got another group reservation request through Reposite from a new planner!

            Are you the right person at your company that handles group reservations?

            Cheers,
            Lee
            ''',

        "campaign == 'Received NMQR' and prior_nmqrs > 0 and quote_lead_goal_mode == 'Needs Response' ": '''
            Hey {lead_first_name} -

            I noticed that you recently received a quote request from a travel planner on Reposite. 

            It appears our travel planner is working on a tight schedule and need a reply today. Here's the link {nmqrurl} to view and reply. 

            Are you the right person at your company that handles group reservations? 

            Cheers,
            Lee
            ''',

        "campaign == 'New QR' and quote_lead_goal_mode != 'Needs Response'": '''
            Hey {lead_first_name} -

            I saw you got another group reservation request through Reposite from a new planner!

            Are you the right person at your company that handles group reservations?

            Cheers,
            Lee
            ''',

        "campaign == 'New QR' and quote_lead_goal_mode == 'Needs Response'": '''
            Hey {lead_first_name} -

            I noticed that you recently received a quote request from a travel planner on Reposite. 

            It appears our travel planner is working on a tight schedule and need a reply today. Here's the link {nmqrurl} to view and reply. 

            Are you the right person at your company that handles group reservations? 

            Cheers,
            Lee
            ''',

        "campaign == 'Token Change'": '''
            Hey {lead_first_name} -

            I saw that you just used tokens to discover new group planners. It's great to see you taking active steps to expand your connections!

            Are there certain types of planners that you're targeting (corporate, student groups, international groups, luxury, etc.)?

            Cheers,
            Lee
            ''',

        "campaign == 'Quote Hotlist'": '''
            Hey {lead_first_name} -

            I noticed that your conversation (with a planner on Reposite) is off to a good start - congrats (though I don't want to jinx it)!

            Are you open to receiving more quotes and group leads from other planners?

            Cheers,
            Lee
            ''',

        "campaign == 'Booking Received'": '''
            Hey {lead_first_name} -

            I noticed that your conversation (with a planner on Reposite) is off to a good start - congrats (though I don't want to jinx it)!

            Are you open to receiving more quotes and group leads from other planners?

            Cheers,
            Lee
            ''',

       "campaign == 'Newly Onboarded'": '''
            Hey {lead_first_name} -

            I saw you just set up an account for {supplier_name} on Reposite! Congrats on being invited by {reseller_org_name}.

            So we can help tailor future leads for you: what's your ideal type of group business (corporate, student groups, international groups, luxury, etc.)?

            Cheers,
            Lee
            '''
    }
    if selection is None:
      return list(initials.keys())
    
    return initials[selection]


def get_initial_message(campaign, prior_nmqrs, quote_lead_goal_mode):
    initial_message =None

    if campaign == 'Received NMQR' and prior_nmqrs in [None, '0', 0] and quote_lead_goal_mode != 'Needs Response' :
        print(f"1 : {campaign} == Received NMQR' and prior_nmqrs == 0 and quote_lead_goal_mode == No need response")
        initial_message = '''Hey {lead_first_name}\n\nI noticed that you recently received your very first quote request from a planner {reseller_org_name} on Reposite - congrats!\nAre you the right person at your company that handles group reservations?\n\nCheers,\n\n{agent_name}'''
    elif campaign == 'Received NMQR' and prior_nmqrs in [None, '0', 0] and quote_lead_goal_mode == 'Needs Response' : 
        print(f"2 :  {campaign} == Received NMQR' and prior_nmqrs == 0 and quote_lead_goal_mode == need response") 
        initial_message = '''Hey {lead_first_name}\n\nI noticed that you recently received your very first quote request from a planner {reseller_org_name} on Reposite - congrats! It appears that they have a tight deadline for response though.\nIf you have availability on {trip_start_date} could you sign up and reply to them today? Here's the link if you lost the initial request {nmqrurl}\n\nCheers,\n\n{agent_name}'''
    elif campaign == 'Received NMQR' and prior_nmqrs not in [None, '0', 0] and quote_lead_goal_mode != 'Needs Response' :
        print(f"3 :  {campaign} == Received NMQR' and prior_nmqrs > 0 and quote_lead_goal_mode == no need response") 
        initial_message = ''' Hey {lead_first_name}\n\nI saw you got another group reservation request through Reposite from a new planner!\nAre you the right person at your company that handles group reservations?\n\n Cheers,\n\n{agent_name}'''
    elif campaign == 'Received NMQR' and prior_nmqrs not in [None, '0', 0] and quote_lead_goal_mode == 'Needs Response' :  
        print(f"4 :  {campaign} == Received NMQR' and prior_nmqrs > 0 and quote_lead_goal_mode ==  need response") 
        initial_message = '''Hey {lead_first_name}\n\nI noticed that you recently received a quote request from a travel planner on Reposite.\nIt appears our travel planner is working on a tight schedule and need a reply today. Here's the link {nmqrurl} to view and reply.\n Are you the right person at your company that handles group reservations? \n\n Cheers,\n\n {agent_name}''' 
    elif campaign == 'New QR' and quote_lead_goal_mode != 'Needs Response' :
        print(f"5 :  {campaign} == New QR' and quote_lead_goal_mode == no need response") 
        initial_message = '''Hey {lead_first_name}\n\nI saw you got another group reservation request through Reposite from a new planner!\n Are you the right person at your company that handles group reservations?\n\n Cheers,\n\n{agent_name}'''
    elif campaign == 'New QR' and quote_lead_goal_mode == 'Needs Response' :  
        print(f"6 :  {campaign} == New QR' and quote_lead_goal_mode == need response") 
        initial_message = '''Hey {lead_first_name}\n\nI noticed that you recently received a quote request from a travel planner on Reposite.\nIt appears our travel planner is working on a tight schedule and need a reply today. Here's the link {nmqrurl} to view and reply.\nAre you the right person at your company that handles group reservations?\n\n Cheers,\n\n{agent_name}'''
    elif campaign == 'Token Change' :  
        print(f"7 :  {campaign} == Token Change") 
        initial_message = '''Hey {lead_first_name}\n\nI saw that you just used tokens to discover new group planners. It's great to see you taking active steps to expand your connections!\nAre there certain types of planners that you're targeting (corporate, student groups, international groups, luxury, etc.)?\n\n Cheers,\n\n{agent_name}''' 
    elif campaign == 'Quote Hotlist' :  
        print(f"8 :  {campaign} == Quote Hotlist") 
        initial_message = '''Hey {lead_first_name}\n\nI noticed that your conversation (with a planner on Reposite) is off to a good start - congrats (though I don't want to jinx it)!\nAre you open to receiving more quotes and group leads from other planners?\n\n Cheers,\n\n{agent_name}'''     
    elif campaign == 'Booking Received' :  
        print(f"9 :  {campaign} == Booking Received") 
        initial_message = ''' Hey {lead_first_name}\n\nI noticed that your conversation (with a planner on Reposite) is off to a good start - congrats (though I don't want to jinx it)!\nAre you open to receiving more quotes and group leads from other planners? \n\n Cheers,\n\n{agent_name}'''    
    elif campaign == 'Newly Onboarded': 
        print(f"10:  {campaign} == Newly Onboarded'") 
        initial_message = '''Hey {lead_first_name}\n\nI saw you just set up an account for {supplier_name} on Reposite! Congrats on being invited by {reseller_org_name}.\n So we can help tailor future leads for you: what's your ideal type of group business (corporate, student groups, international groups, luxury, etc.)?\n\n Cheers,\n\n{agent_name}'''       
    return initial_message
