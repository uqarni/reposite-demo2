
import streamlit as st
from functions import ideator, initial_text_info
import json
import os
import sys
from datetime import datetime
from supabase import create_client, Client
from reminderwrapper import run_conversation

# connect to supabase database
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
    st.title("Taylor RAG 10 Pairs")
    st.write("To test, first select some fields then click the button below.")

    # variables for system prompt
    bot_name = 'Taylor'
    membership_link = 'https://www.reposite.io/membership-overview-1'

    # variables about the lead
    email = st.text_input('email', value='john@doe.com')
    supplier_name = st.text_input('supplier name', value='Acme Trading Co')
    lead_first_name = st.text_input('Lead First Name', value='John')
    lead_last_name = st.text_input('Lead Last Name', value='Doe')
    nmqr_count = st.text_input('# NMQR received', value='10')
    nmqrurl = 'nmqrurl.com'
    # most recent nmqr info
    reseller_org_name = st.text_input('reseller org name', value='Smith Co')
    category = st.text_input('category', value='travel')
    date = st.text_input('date', value='June 20, 2023')
    current_date = now
    destination = st.text_input('destination', value='Honolulu')
    group_size = st.text_input('group size', value='50')
    trip_dates = st.text_input(
        'trip dates', value='August 10, 2023 to August 20, 2023')

    options = initial_text_info()
    initial_text_choice = st.selectbox(
        "Select initial email template", options)

    # initial_text = bot_info['initial_text']
    # initial_text = initial_text.format(bot_name = bot_name, nmqr_count = nmqr_count, lead_first_name = lead_first_name, reseller_org_name = reseller_org_name, supplier_name = supplier_name)

    # need to push this then make sure it works
    if st.button('Click to Start or Restart'):
        with open('day.txt', 'w') as f:
            f.truncate(0)
        initial_text = initial_text_info(initial_text_choice)
        # if initial_text_choice == options[0] or initial_text_choice == options[1]:
        #     data, count = supabase.table("bots_dev").select("*").eq("id", "TaylorNMQR").execute()
        # else:
        #     data, count = supabase.table("bots_dev").select("*").eq("id", "taylor").execute()

        res = supabase.table("bots_dev").select(
            "*").eq("id", "taylorRAG").execute()
        data, count = res.data, None
        bot_info = data[0]
        initial_text = initial_text.format(lead_first_name=lead_first_name, reseller_org_name=reseller_org_name,
                                           supplier_name=supplier_name, category=category, destination=destination)

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
            "nmqrurl": nmqrurl
        }
        file_path = 'lead_dict_info.json'
        with open(file_path, 'w') as f:
            json.dump(lead_dict_info, f)

        system_prompt = bot_info['system_prompt']
        system_prompt = system_prompt.format(**lead_dict_info)

        # st.write(initial_text)
        restart_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('database.jsonl', 'r') as db, open('archive.jsonl', 'a') as arch:
            # add reset
            arch.write(json.dumps({"restart": restart_time}) + '\n')
        # copy each line from db to archive
            for line in db:
                arch.write(line)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": initial_text}
        ]
        st.session_state["messages"] = messages

        # clear database to only first two lines
        with open('database.jsonl', 'w') as f:
            # Override database with initial json files
            f.write(json.dumps(messages[0])+'\n')
            f.write(json.dumps(messages[1])+'\n')

    # initialize messages list and print opening bot message
    # st.write("Hi! This is Tara. Seems like you need help coming up with an idea! Let's do this. First, what's your job?")

    # Create a text input for the user to enter their message and append it to messages

    if 'editing' not in st.session_state:
        st.session_state['editing'] = False
    if 'pre_last_message' not in st.session_state:
        st.session_state['pre_last_message'] = ""
    if 'last_bot_message' not in st.session_state:
        st.session_state['last_bot_message'] = ""
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    # Create an edit button
    editButtonText = "Edit Bot Response"
    if st.session_state['editing']:
        editButtonText = "Submit As Correction"

    def toggle_editing_state():
        # Toggle editing state
        print("Edit button clicked")
        st.session_state['editing'] = not st.session_state['editing']
        if st.session_state['editing']:
            editButtonText = "Submit"
        else:
            editButtonText = "Edit"
            # st
            # Toggle editing state
            # st.session_state['editing'] = not st.session_state['editing']
            # TODO: Send message to Supabase
            # supabase.table("")
            # TODO: Write to local db

    # Display text or textbox based on editing state

    # def writeMessages():
    if st.session_state['editing'] and len(st.session_state["messages"]) > 0:
        # st.write("Editing")
        messages_to_display = ""
        for message in st.session_state["messages"][1:-1]:
            messages_to_display = messages_to_display + \
                message["role"] + ": " + message["content"] + "\n\n"
        st.write(messages_to_display)

        modified_message = st.session_state["messages"][-1]
        temp = st.text_area(
            "Edit your message", value=modified_message["content"], height=500
        )
        st.session_state["messages"][-1]["content"] = temp
    elif len(st.session_state["messages"]) > 0:
        # st.write("Not Editing")

        # TODO: Clean this input up
        messages_to_display = ""
        for message in st.session_state["messages"][1:]:
            messages_to_display = messages_to_display + \
                message["role"] + ": " + message["content"] + "\n\n"
        st.write(messages_to_display)
        # st.write(st.session_state["messages"][1:])

    # writeMessages()

    userresponse = st.text_area("Enter your message")
    # Create a button to submit the user's message
    if st.button("Send"):

        print("Send button clicked")
        # get dict info to populate
        file_path = 'lead_dict_info.json'
        with open(file_path, 'r') as f:
            lead_dict_info = json.load(f)

        # prep the json
        newline = {"role": "user",
                   "content": userresponse.format(**lead_dict_info)}
        # append to database
        with open('database.jsonl', 'a') as f:
            # Write the new JSON object to the file
            f.write(json.dumps(newline) + '\n')
        st.session_state["messages"].append(newline)
        # extract messages out to list
        messages = []

        with open('database.jsonl', 'r') as f:
            for line in f:
                json_obj = json.loads(line)
                messages.append(json_obj)

        # generate OpenAI response
        messages, count = ideator(messages, lead_dict_info)

        # append to database
        with open('database.jsonl', 'a') as f:
            for i in range(count):
                f.write(json.dumps(messages[-count + i]) + '\n')

        # Display the response in the chat interface

        st.session_state["messages"].append(messages[-1])
        print("Messages: ", st.session_state["messages"], "\n\n")
        st.experimental_rerun()
        # writeMessages()
        # oldMessage = ""
        # for i, message in enumerate(messages[1:-1]):
        #     if "[secret internal thought" not in str(message):
        #         oldMessage = oldMessage + message["role"] + \
        #             ": " + message["content"] + "\n\n"
        # newMessage = messages[-1]["role"] + \
        #     ": " + messages[-1]["content"] + "\n\n"
        # st.session_state['pre_last_message'] = oldMessage
        # st.session_state['last_bot_message'] = newMessage
        # print("Pre last message: \n", st.session_state['pre_last_message'])
        # print("Last bot message: \n", st.session_state['last_bot_message'])

        # print("Pre last message: \n" + string)
        # print("Last bot message: \n" + newMessage)

    st.button(editButtonText,
              on_click=(lambda: toggle_editing_state()))

    # TODO: Refactor this to work with above changes
    if st.button("Increment 3 Days"):
        # read day.txt
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

        newline = {"role": "assistant",
                   "content": "[secret internal thought; the User cannot see this message] 3 days have gone by since the lead responded to me. I should followup with a super short email pitching the benefits of the premium Reposite membership, ending with a question."}

        # append to database
        with open('database.jsonl', 'a') as f:
            # Write the new JSON object to the file
            f.write(json.dumps(newline) + '\n')

        # extract messages out to list
        messages = []

        with open('database.jsonl', 'r') as f:
            for line in f:
                json_obj = json.loads(line)
                messages.append(json_obj)

        # check run_conversation
        checkit = run_conversation(messages[1:-1])
        if checkit == 'yes':
            # generate OpenAI response
            file_path = 'lead_dict_info.json'
            with open(file_path, 'r') as f:
                lead_dict_info = json.load(f)
            messages, count = ideator(messages, lead_dict_info)

            # append to database
            with open('database.jsonl', 'a') as f:
                for i in range(count):
                    f.write(json.dumps(messages[-count + i]) + '\n')

            # Display the response in the chat interface
            string = ""

            for message in messages[1:]:
                if "[secret internal thought" not in str(message):
                    string = string + message["role"] + \
                        ": " + message["content"] + "\n\n"
            if day == 3 or day == 6:
                st.write(string)
                st.write(f'*Day {day}*')
            elif day == 9:
                st.write('max followups reached. please reset')
        elif checkit == 'no':
            print('followup not warranted')


if __name__ == '__main__':
    main()
