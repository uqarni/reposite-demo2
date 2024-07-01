
import streamlit as st
from functions2 import ideator, initial_text_info,get_initial_message
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
    all_new_messages = []

    # Create a title for the chat interface
    st.title("Taylor / Lee")
    st.write("To test, first select some fields then click the button below.")
  
    campiagnOptions = ['Received NMQR', 'New QR', 'Token Change', 'Quote Hotlist', 'Booking Received', 'Newly Onboarded']

    #variables about the lead
    email = st.text_input('email', value = 'john@doe.com')
    supplier_name = st.text_input('Supplier name', value = 'Acme Trading Co')
    lead_first_name = st.text_input('Lead First Name', value = 'John')
    lead_last_name = st.text_input('Lead Last Name', value = 'Doe')
    nmqr_count = st.text_input('NMQR received', value = '0')
    campaign = st.selectbox("Select Campaign", campiagnOptions)
    quote_lead_goal_mode = st.selectbox("Quote Lead Goal Mode", options = ["No Response Needed", "Needs Response"], index = 0)
    # campaign = st.text_input('Campaign', value = '0')
    nmqrurl = 'nmqrurl.com'
    
    #most recent nmqr info
    reseller_org_name = st.text_input('reseller org name', value = 'Smith Co')
    category = st.text_input('category', value = 'travel')
    date = st.text_input('date', value = 'June 20, 2023')
    current_date = now
    destination = st.text_input('destination', value = 'Honolulu')
    group_size = st.text_input('group size', value = '50')
    trip_dates = st.text_input('trip dates', value = 'August 10, 2023 to August 20, 2023')
    market = st.selectbox('Market', options = ['TM', 'NTM'], index = 0)

    

    # options = initial_text_info()
    # initial_text_choice  = st.selectbox("Select initial email template", options)
    

    
    #initial_text = bot_info['initial_text']
    #initial_text = initial_text.format(bot_name = bot_name, nmqr_count = nmqr_count, lead_first_name = lead_first_name, reseller_org_name = reseller_org_name, supplier_name = supplier_name)
    
    #need to push this then make sure it works
    if st.button('Click to Start or Restart'):

        with open('database.jsonl', 'w') as f:
            pass 

        with open('bot.txt', 'w') as f:
            pass


        if campaign == 'Received NMQR' and quote_lead_goal_mode == "Needs Response":
            data, count = supabase.table("bots_dev").select("*").eq("id", "nonmember_respond").execute() 
            bot_used = 'nonmember_respond'
            print('nonmember_respond used!!!')

        elif campaign != 'Received NMQR' and quote_lead_goal_mode == "Needs Response":
            data, count = supabase.table("bots_dev").select("*").eq("id", "member_respond").execute() 
            bot_used = 'member_respond'  
            print('member_respond used!!!')       

        elif campaign == 'Received NMQR' and quote_lead_goal_mode != "Needs Response":
            data, count = supabase.table("bots_dev").select("*").eq("id", "nonmember_signup").execute() 
            bot_used = 'nonmember_signup'
            print('nonmember_signup used!!!')
            
        elif campaign not in ['', None]:
            bot_used = 'member_upgrade'
            data, count = supabase.table("bots_dev").select("*").eq("id", "member_upgrade").execute() 
            print("member_upgrade used!!!")

        with open('bot.txt', 'w') as file:
            file.write(bot_used)



        bot_info = data[1][0]
        initial_text = get_initial_message(campaign,nmqr_count,quote_lead_goal_mode)

        if market == 'NTM':
            # TAYLOR
            price = '$500'
            agent_name = 'Taylor'
            membership_link = 'https://www.reposite.io/membership-overview-1'
            demo_link = 'https://guides.reposite.io/membership-gated-supplier-demo-0'
            calendar_link =   'https://meetings.salesloft.com/reposite/brendanhollingsworth'
        else:
            # LEE
            price = '$1000'
            agent_name = 'Lee'
            membership_link = 'https://www.reposite.io/membership-overview-tier1?sbrc=1Bd7h_suhk2WBfAu-UimW4A%3D%3D%24FZq3JqgS-62UZupynn2WTQ%3D%3D'
            demo_link = 'https://guides.reposite.io/membership-gated-supplier-demo'
            calendar_link =   'https://calendar.app.google/QgHc7RqZKFoHsWXr5'
 
        print("-------->> initial ", initial_text)

        def get_date_before_to(date_range):

            if "to" in date_range:
                return date_range.split("to")[0].strip()
            return 'date'
        
        trip_start_date = get_date_before_to(trip_dates)

        initial_text = initial_text.format(lead_first_name = lead_first_name, reseller_org_name = reseller_org_name, supplier_name = supplier_name, category = category, destination = destination, agent_name= agent_name, nmqrurl=nmqrurl, trip_start_date =trip_start_date)

        print('agent_name: ', agent_name)   

        lead_dict_info = {
            "agent_name": agent_name,
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
            "demo_link": demo_link,
            "price":price,
            "calendar_link": calendar_link,
            "nmqr_signup_video": "https://www.screencast.com/t/mnVdphydqsq", # confirmed
            "login_link": "https://app.reposite.io/suppliers?auth=login", # confirmed
            "signup_link": "https://app.reposite.io/suppliers?auth=signUp", # confirmed
        }
  
        file_path = 'lead_dict_info.json'
        with open(file_path, 'w') as f:
            json.dump(lead_dict_info, f)
    
        system_prompt = bot_info['system_prompt']
        system_prompt = system_prompt.format(**lead_dict_info)

        st.write(initial_text, unsafe_allow_html = True)
        # st.markdown(string,)
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
            print("\n----------", message)
            if "[secret internal message]" not in str(message):
                string = string + message["role"] + ": " + message["content"] + "<br><br>"

        st.markdown(string, unsafe_allow_html = True)
            
    if st.button("Send Followup"):


        secret_message = "[secret internal message] Hi {agent_name}, this is Heather, the CEO of Reposite. The lead you've been emailing hasn't responded in 3 days. Reply to this message with a followup email to the  lead. Remember, the lead doesn't see this message. Do not acknowledge it in your response. Make the followups shorter, max 3 sentences."
       
        file_path = 'lead_dict_info.json'
        with open(file_path, 'r') as f:
            lead_dict_info = json.load(f)

        newline = {"role": "assistant", "content": secret_message.format(**lead_dict_info)}
        
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
 
         
            with open('bot.txt', 'r') as file:
                bot_to_use = file.read()
                print('bot to use is ', bot_to_use)

            messages, count = ideator(messages, lead_dict_info,bot_to_use)

            #append to database
            with open('database.jsonl', 'a') as f:
                for i in range(count):
                    f.write(json.dumps(messages[-count + i]) + '\n')

            # Display the response in the chat interface
            string = ""
            for message in messages[1:]:
                if "[secret internal message]" not in message.get('content'):
                    string = string + message["role"] + ": " + message["content"] + "<br><br>"
            
            st.markdown(string, unsafe_allow_html = True)
      
        elif checkit == 'no':
            print('followup not warranted')


if __name__ == '__main__':
    main()

