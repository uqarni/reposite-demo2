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




def find_examples(query, k=8):
    loader = CSVLoader(file_path="Reposite Examples - just inputs.csv")

    data = loader.load()
    embeddings = OpenAIEmbeddings()


    db = FAISS.from_documents(data, embeddings)
    query = "I dont see any leads when I click on the link." 
    examples = ''
    docs = db.similarity_search(query, k)
    df = pd.read_csv('Reposite Examples - Taylor Examples.csv')
    i = 1
    for doc in docs:
        input_text = doc.page_content[14:]
        row = doc.metadata['row']


        lookup_value = input_text  # The value you want to look up in column 1

        df = pd.read_csv('Reposite Examples - Taylor Examples.csv')
        try:
            output = df.loc[df['User Message'] == lookup_value, 'Assistant Message'].iloc[0]
        except:
            print('found error for input')

        examples += f'Example {i}: \n\nLead Email: {input_text} \n\nTaylor Response: {output} \n\n'
        i += 1
    return examples

    
#generate openai response; returns messages with openai response
def ideator(messages):
    print('message length: ' + str(len(messages)))
    prompt = messages[0]['content']
    messages = messages[1:]
    new_message = messages[-1]['content']

    #perform similarity search
    examples = find_examples(new_message, k=5)
    prompt = prompt + '\n\n' + examples
    prompt = {'role': 'system', 'content': prompt}
    messages.insert(0,prompt)
    
    for i in range(5):
      try:
        key = os.environ.get("OPENAI_API_KEY")
        openai.api_key = key
    
        result = openai.ChatCompletion.create(
          model="gpt-4",
          messages= messages
        )
        response = result["choices"][0]["message"]["content"]
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



def initial_text_info(selection=None):
    dictionary = {
        'NTM $500 Membership - Received NMQR | First': '''
        Hey {FirstName} -

I noticed that you recently received your very first quote request from a planner {Quote_Lead_Company_Name} on Reposite - congrats!

Are you the right person at {Supplier_Organization_Name} that handles group reservations?

Cheers,
Taylor
''',

        'NTM $500 Membership - Received NMQR | Subsequent':'''
        Hey {FirstName} -

I saw you got another group reservation request through Reposite from {Quote_Lead_Company_Name}!

Are you the right person at {Supplier_Organization_Name} that handles group reservations?

Cheers,
Taylor
''',

        'NTM $500 Membership - Newly Onboarded': '''
        Hey {FirstName} -

I saw you just set up an account for {Supplier_Organization_Name} on Reposite! Congrats on being invited by {Quote_Lead_Company_Name}.

So we can help tailor future leads for you: what's your ideal type of group business (corporate, student groups, international groups, luxury, etc.)?

Cheers,
Taylor
''',

        'NTM $500 Membership - New QR':'''
        Hey {FirstName} -

I saw that your Reposite profile just sparked some new interest! A planner {Quote_Lead_Company_Name}, just sent you a new quote request - they're looking for {Category} suppliers in {Quote_Lead_Destination}.

Based on the details, do you feel like this lead is relevant for {Supplier_Organization_Name}?

Cheers,
Taylor
''',

        'NTM $500 Membership - Token Change':'''
Hey {FirstName} -

I saw that you just used tokens to discover new group planners. It's great to see you taking active steps to expand your connections!

Are there certain types of planners that you're targeting (corporate, student groups, international groups, luxury, etc.)?

Cheers,
Taylor
''',
        'NTM $500 Membership - Quote Hotlist':'''
Hey {FirstName} -

I noticed that your conversation with {Quote_Lead_Company_Name} is off to a good start - congrats (though I don't want to jinx it)!

Are you open to receiving more quotes and group leads from other planners?

Cheers,
Taylor
''',
        'NTM $500 Membership - Booking Received': '''
Hey {FirstName} -

Congrats on your recent booking with {Quote_Lead_Company_Name}! Was everything up to your expectations?

Best,
Taylor
'''
    }
    if selection is None:
      return list(dictionary.keys())
    
    return dictionary[selection]


test = find_examples('I dont see any quote when I log in')
print(test)