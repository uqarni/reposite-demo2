
import streamlit as st
from functions import ideator, initial_text_info
import json
import os
import sys
from datetime import datetime
from supabase import create_client, Client

#connect to supabase database
urL: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(urL, key)


# id
# org_id
# system_prompt
# max_followup_count
# followup_time
# followup_prompt
now = datetime.now()
now = now.strftime("%Y-%m-%d %H:%M:%S")



def main():

    # Create a title for the chat interface
    st.title("Reposite Bot (named Taylor)")
    st.write("To test, first select some fields then click the button below.")
  
    #variables for system prompt
    bot_name = 'Taylor'
    membership_link = 'https://www.reposite.io/membership-overview-1'

    #variables about the lead
    email = st.text_input('email', value = 'john@doe.com')
    supplier_name = st.text_input('supplier name', value = 'Acme Trading Co')
    lead_first_name = st.text_input('Lead First Name', value = 'John')
    lead_last_name = st.text_input('Lead Last Name', value = 'Doe')
    nmqr_count = st.text_input('# NMQR received', value = '10')
    nmqrurl = 'nmqrurl.com'
    #most recent nmqr info
    reseller_org_name = st.text_input('reseller org name', value = 'Smith Co')
    category = st.text_input('category', value = 'travel')
    date = st.text_input('date', value = 'June 20, 2023')
    current_date = now
    destination = st.text_input('destination', value = 'Honolulu')
    group_size = st.text_input('group size', value = '50')
    trip_dates = st.text_input('trip dates', value = 'August 10, 2023 to August 20, 2023')
    
    options = initial_text_info()
    initial_text_choice  = st.selectbox("Select initial email template", options)
    

    
    #initial_text = bot_info['initial_text']
    #initial_text = initial_text.format(bot_name = bot_name, nmqr_count = nmqr_count, lead_first_name = lead_first_name, reseller_org_name = reseller_org_name, supplier_name = supplier_name)
    
    #need to push this then make sure it works
    if st.button('Click to Start or Restart'):
        initial_text = initial_text_info(initial_text_choice)
        if initial_text_choice == options[0] or initial_text_choice == options[1]:
            data, count = supabase.table("bots_dev").select("*").eq("id", "TaylorNMQR").execute()
        else:
            data, count = supabase.table("bots_dev").select("*").eq("id", "taylor").execute()
        bot_info = data[1][0]
        initial_text = initial_text.format(FirstName = lead_first_name, Quote_Lead_Company_Name = reseller_org_name, Supplier_Organization_Name = supplier_name, Category = category, Quote_Lead_Destination = destination)
        
    
        system_prompt = bot_info['system_prompt']
        system_prompt = system_prompt.format(
            #bot info
            bot_name=bot_name, 
            membership_link=membership_link,
            #lead info
            email=email, 
            supplier_name=supplier_name, 
            lead_first_name=lead_first_name, 
            lead_last_name=lead_last_name, 
            nmqr_count=nmqr_count, 
            #most recent nmqr info
            reseller_org_name=reseller_org_name, 
            category=category, 
            date=date, 
            current_date=current_date, 
            destination=destination, 
            group_size=group_size,  # Note: You used 'date' for both 'date' and 'group size'
            trip_dates=trip_dates,
            nmqrurl = nmqrurl
        )
        st.write(initial_text)
        restart_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('database.jsonl', 'r') as db, open('archive.jsonl','a') as arch:
        # add reset 
            arch.write(json.dumps({"restart": restart_time}) + '\n')
        #copy each line from db to archive
            for line in db:
                arch.write(line)

        #clear database to only first two lines
        with open('database.jsonl', 'w') as f:
        # Override database with initial json files
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": initial_text}            
            ]
            f.write(json.dumps(messages[0])+'\n')
            f.write(json.dumps(messages[1])+'\n')



    #initialize messages list and print opening bot message
    #st.write("Hi! This is Tara. Seems like you need help coming up with an idea! Let's do this. First, what's your job?")

    # Create a text input for the user to enter their message and append it to messages
    userresponse = st.text_area("Enter your message")
    

    # Create a button to submit the user's message
    if st.button("Send"):
        #prep the json
        newline = {"role": "user", "content": userresponse}
        
        #append to database
        with open('database.jsonl', 'a') as f:
        # Write the new JSON object to the file
            f.write(json.dumps(newline) + '\n')

        #extract messages out to list
        messages = []

        with open('database.jsonl', 'r') as f:
            for line in f:
                json_obj = json.loads(line)
                messages.append(json_obj)

        #generate OpenAI response
        messages, count = ideator(messages)

        #append to database
        with open('database.jsonl', 'a') as f:
                for i in range(count):
                    f.write(json.dumps(messages[-count + i]) + '\n')



        # Display the response in the chat interface
        string = ""

        for message in messages[1:]:
            string = string + message["role"] + ": " + message["content"] + "\n\n"
        st.write(string)
            

if __name__ == '__main__':
    main()

