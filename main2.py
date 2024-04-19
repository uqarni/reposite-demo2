
import streamlit as st
from functions2 import ideator, initial_text_info
import json
import os
import sys
from datetime import datetime
from supabase import create_client, Client
from reminderwrapper import run_conversation

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
    st.title("Taylor RAG 4 Full Convos")
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
    quote_lead_goal_mode = st.selectbox("Quote Lead Goal Mode", options = ["No Response Needed", "Needs Response"], index = 0)
    #most recent nmqr info
    reseller_org_name = st.text_input('reseller org name', value = 'Smith Co')
    category = st.text_input('category', value = 'travel')
    date = st.text_input('date', value = 'June 20, 2023')
    current_date = now
    destination = st.text_input('destination', value = 'Honolulu')
    group_size = st.text_input('group size', value = '50')
    trip_dates = st.text_input('trip dates', value = 'August 10, 2023 to August 20, 2023')
    market = st.selectbox('Market', options = ['TM', 'NTM']
    
    options = initial_text_info()
    initial_text_choice  = st.selectbox("Select initial email template", options)
    

    
    #initial_text = bot_info['initial_text']
    #initial_text = initial_text.format(bot_name = bot_name, nmqr_count = nmqr_count, lead_first_name = lead_first_name, reseller_org_name = reseller_org_name, supplier_name = supplier_name)
    
    #need to push this then make sure it works
    if st.button('Click to Start or Restart'):
        with open('bot.txt', 'w') as f:
            f.truncate(0)
        initial_text = initial_text_info(initial_text_choice)
        # if initial_text_choice == options[0] or initial_text_choice == options[1]:
        #     data, count = supabase.table("bots_dev").select("*").eq("id", "TaylorNMQR").execute()
        # else:
        #     data, count = supabase.table("bots_dev").select("*").eq("id", "taylor").execute()

        if initial_text == initial_text_info('NMQR Received') and quote_lead_goal_mode == "Needs Response":
            data, count = supabase.table("bots_dev").select("*").eq("id", "taylorSupplerUpgrade_RAG").execute() 
            bot_used = 'taylorSupplerUpgrade_RAG'
            print('taylorSupplerUpgrade_RAG used!!!')

        elif quote_lead_goal_mode == "Needs Response":
            data, count = supabase.table("bots_dev").select("*").eq("id", "taylorSupplier_RAG").execute() 
            bot_used = 'taylorSupplier_RAG'  
            print('taylorSupplier_RAG used!!!')       

        elif initial_text == initial_text_info('NMQR Received'):
            data, count = supabase.table("bots_dev").select("*").eq("id", "taylorRAG").execute() 
            bot_used = 'taylorNMQR_RAG'
            print('taylorNMQR used!!!')
            
        else:
            #usingTAYLOR for non-NMQR RAG
            bot_used = 'taylor_RAG'
            data, count = supabase.table("bots_dev").select("*").eq("id", "taylor").execute() 
            print("taylor used!!!")

        with open('bot.txt', 'w') as file:
            file.write(bot_used)

        bot_info = data[1][0]
        initial_text = initial_text.format(lead_first_name = lead_first_name, reseller_org_name = reseller_org_name, supplier_name = supplier_name, category = category, destination = destination)
        if market == 'NTM':
            price = '$500'
        else:
            price = '$1000'
            
        lead_dict_info = {
            "bot_name": bot_name,
            "membership_link": membership_link,
            "email": email,
            "supplier_name": supplier_name,
            "lead_first_name": lead_first_name,
            "lead_last_name": lead_last_name,
            "nmqr_count": nmqr_count,
            "reseller_org_name": reseller_org_name,
            "category": category,
            "date": date,
            "current_date": current_date,
            "destination": destination,
            "group_size": group_size,
            "trip_dates": trip_dates,
            "nmqrurl": nmqrurl,
            "ntm_link": "https://www.reposite.io/membership-overview-1",
            "ntm_demo": "https://guides.reposite.io/membership-gated-supplier-demo-0",
            "brendan_calendar": "https://meetings.salesloft.com/reposite/brendanhollingsworth",
            "nmqr_signup_video": "https://www.screencast.com/t/mnVdphydqsq",
            "login_link": "https://app.reposite.io/suppliers?auth=login",
            "signup_link": "https://app.reposite.io/suppliers?auth=signUp",
            "price": price
        }
        file_path = 'lead_dict_info.json'
        with open(file_path, 'w') as f:
            json.dump(lead_dict_info, f)
    
        system_prompt = bot_info['system_prompt']
        system_prompt = system_prompt.format(**lead_dict_info)

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


        #get dict info to populate
        file_path = 'lead_dict_info.json'
        with open(file_path, 'r') as f:
            lead_dict_info = json.load(f)

        #prep the json
        newline = {"role": "user", "content": userresponse.format(**lead_dict_info)}
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
        #pull bot used
        with open('bot.txt', 'r') as file:
            bot_to_use = file.read()
            print('bot to use is ', bot_to_use)
        messages, count = ideator(messages, lead_dict_info, bot_to_use)

        #append to database
        with open('database.jsonl', 'a') as f:
                for i in range(count):
                    f.write(json.dumps(messages[-count + i]) + '\n')

        # Display the response in the chat interface
        string = ""

        for message in messages[1:]:
            if "[secret internal thought" not in str(message):
                string = string + message["role"] + ": " + message["content"] + "<br><br>"
        st.markdown(string, unsafe_allow_html = True)
            
    if st.button("Increment 3 Days"):
        #read day.txt
        with open('day.txt', 'r+') as f:
            content = f.read().strip()
            
            if not content:
                f.seek(0)
                f.write('3')
                day = 3
            elif content == '3':
                f.seek(0)
                f.truncate()
                f.write('6')
                day = 6
            elif content == '6':
                day = 9

        newline = {"role": "assistant", "content": "[secret internal thought; the User cannot see this message] 3 days have gone by since the lead responded to me. I should followup with a super short email pitching the benefits of the premium Reposite membership, ending with a question."}
        
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

        #check run_conversation
        checkit = run_conversation(messages[1:-1])
        if checkit == 'yes':
            #generate OpenAI response
            file_path = 'lead_dict_info.json'
            with open(file_path, 'r') as f:
                lead_dict_info = json.load(f)
            messages, count = ideator(messages, lead_dict_info)

            #append to database
            with open('database.jsonl', 'a') as f:
                    for i in range(count):
                        f.write(json.dumps(messages[-count + i]) + '\n')

            # Display the response in the chat interface
            string = ""

            for message in messages[1:]:
                if "[secret internal thought" not in str(message):
                    string = string + message["role"] + ": " + message["content"] + "\n\n"
            if day == 3 or day == 6:
                st.markdown(string, unsafe_allow_html = True)
                st.write(f'*Day {day}*')
            elif day == 9:
                st.write('max followups reached. please reset')
        elif checkit == 'no':
            print('followup not warranted')
if __name__ == '__main__':
    main()

