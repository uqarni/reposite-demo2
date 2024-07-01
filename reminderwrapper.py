import openai
import json


def followup(yesno):
    if yesno == 'yes':
        return 'y'
    if yesno == 'no':
        return 'n'
    else:
        return 'n'



########
functions=[
            {
                "name": "followup",
                "description": "Analyze the conversation provided by the user and determine if a followup is warranted",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "yesno": {
                            "type": "string",
                            "enum": ["yes", "no"],
                            "description": "yes if a follow up is warranted, and no if it is not",
                        }
                    },
                    "required": ["yesno"],
                },
            }
        ]



# Step 1, send model the user query and what functions it has access to
def run_conversation(bot_messages):

    prompt = '''
    You work in the sales department for Reposite, a travel agency and experience supplier marketplace.
    Your job is to analyze the conversation between our sales agent (the Assistant) and the potential customer (the User) and determine if a follow-up is warranted. 

    A follow-up is NOT warranted if:
    (1) the user has indicated that they are not interested or are unhappy in some way. For example, they have said that they are not interested in the product or do not want to be contacted.
    (2) the user has indicated that they already purchased the Reposite membership.
    

    Otherwise, a follow-up is warranted. 

    If a follow-up is warranted, execute the followup() function with 'yes' as the input. If a follow-up is not warranted, execute the followup() function with "no" as the input.
    '''
    all_messages = [{'role': 'system', 'content': prompt}]
    
    #for iterate through redis database of all the conversations thus far:
    all_messages.append({"role": "user", "content": str(bot_messages)})
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=all_messages,
        functions=functions,
        function_call= {"name": "followup"}

    )

    message = response["choices"][0]["message"]

    # Step 2, check if the model wants to call a function
    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        return json.loads(message["function_call"]["arguments"])["yesno"]
    else:
        return 'error'


# Step 1, send model the user query and what functions it has access to
def responder_run_conversation(bot_messages, agent_name):
    try:
        representative = agent_name

        prompt = f'''
            You work for Reposite, a marketplace that connects travel agents and group event suppliers. Your job is to look at the following conversation and determine if {representative}, our sales rep, should follow up with the lead or not. Output yes if she should, no if she should not.


            Focus on the lead's latest message.
            Output 'yes' if {representative} should respond.
            For example, if they provide an answer to {representative}'s question or ask their own question.
            
            Output 'no' if, in their most recent message, the user has indicated that they are not interested or are unhappy/dissatisfied in some way.
            For example, if they have said stop, unsubscribe, or do not want to be contacted.
            
            Below are some examples. Make sure you prioritize the lead's latest message when judging whether or not {representative} should respond.

            EXAMPLE 1: output = no
            {representative}: Hi Bill, I see you got a new job from the Reposite platform. Are you the right person from Company X to speak with about this? Best, {representative}
            Lead: Hi {representative}, please stop messaging me
            
            EXAMPLE 2: output = no
            {representative}: Hey Sally -I saw you just set up an account for Axe Throwing Austin on Reposite! Congrats on being invited by Tahir Travel Agents Inc. So we can help tailor future leads for you: what's your ideal type of group business (corporate, student groups, international groups, luxury, etc.)? Cheers, {representative}
            Lead: I am sick and tired of all these emails. Please take me off of your email listing immediately.
            
            EXAMPLE 3: output = yes
            {representative}: Hi Ryan, I see you got a new job from the Reposite platform. Are you the right person from Company X to speak with about this? Best, {representative}
            Lead: Hi {representative}, yes I am the right person to speak with about this. Can you tell me more about how we can get more leads?
            
            EXAMPLE 4: output = yes
            {representative}: Hey Jeremy -Congrats on your recent booking with International Travel Co! Was everything up to your expectations? Best, {representative}
            Lead: I had some questions about getting more leads. Is there someone we could get on a call with?
            
            EXAMPLE 5: output = yes
            {representative}: Hey Jeremy As a member of Reposite, you'll gain access to a network of over 2,100+ professional planners who plan all types of corporate and luxury travel, leisure group travel, and private events. This could potentially lead to an increase in your group business, hence resulting in increased revenue. Best, {representative}
            Lead: Stop emailing me please. Take me off.
            Lead: Hi, can you actually tell me more?

            EXAMPLE 6: output = no
            {representative}: Membership also gives you unlimited access to quote on Requests for Proposals (RFPs), allowing you to seize every opportunity that matches your business. Additionally, you'll be discoverable by our network of planners, enhancing your visibility and therefore your chances of securing more group business. \n\nTo further set you up for success, we provide educational resources led by renowned travel trade experts. Regards, {representative}
            Lead: dont email me i hate you.
            Lead: Hi, can you actually tell me more?
            {representative}: Certainly, Jeremy. What would you like to know?'
            Lead: nevermind stop emailing me

            EXAMPLE 7: output = yes
            {representative}: Hi Jessica, I'm sorry, I don't have the specific date information available at this moment. To gain full details of the trip, including the trip dates, I recommend logging into your Reposite account and checking the quote request there. Let me know if you need any further assistance.Best, {representative}
            Lead: Hi {representative},No worries, I was able to get to my computer and respond to the request. Thanks so much. Jessica

            EXAMPLE 8: output = yes
            Lead : Hello {representative}, Thank you for your inquiry. We are pleased that your group is interested in visiting  The Legacy Sites <https://legacysites.eji.org/>.

            Please contact Guest Services at (334) 386-9100 to begin planning your group visit. We will be glad to help ensure that your group can enter the museum together, as the entry to the Legacy Museum is by timed entry ticket. The
            National Memorial for Peace and Justice is a general admission ticket, valid for entry anytime during operating hours.

            We do not offer special group rates or discounts, but student and senior (62+) tickets are already available at a discounted rate. The combination ticket (for entry to both the museum and memorial) is also discounted.
            
            EXAMPLE 9: output = yes
            Lead : Hello {representative}, I do appreciate your tenacity. My company is only me at the moment. I do not have the resources to accommodate large parties.
            I am a walking historic tour company. Not really on the tippitty-top of corporate agenda outings.Hit me up in one year. Let’s see what I can do for you then. I do LOVE the idea of your company. Freaking brilliant!
            

            EXAMPLE 10: output = yes
            Lead : Hello {representative}, I do not have this app so I have not seen this request. Out form is on our website.

            EXAMPLE 11: output = yes
            Lead : Good day {representative}, Thank you for contacting. Yes, we handle group reservations. We would be more than happy to check prices and service availability for you. Please send us the following information:
            - Flight details ( flight number and service date)
            - Luggage amount
            - Number of passengers
            Looking forward to hearing from you


            EXAMPLE 12: output = yes
            Lead : Hi {representative}, We're not sure what quote you are referring to. Can you please clarify? Thank you


            EXAMPLE 13: output = yes
            Lead : Hi {representative},Introducing you to Danielle Brackett – Group Sales Manager for Leisure market and Heidi Burns – Group Sales manager for Corporate business. They will be your point of contact for group reservations.

            
            EXAMPLE 14: output = yes
            Lead : Thanks {representative}, I look forward to working with you all.  We have submitted a bid with you already, so hopefully we will be able to get that business! We appreciate you and your company!

            EXAMPLE 15: output = yes
            Lead : Hi {representative},Can you forward his request here? Thank you. Warm Regards.

        '''


    
        all_messages = [{'role': 'system', 'content': prompt}]
        
        #for iterate through redis database of all the conversations thus far:
        all_messages.append({"role": "user", "content": f"Hey Boss - heres my message history so far. I am the assistant. Should I respond?\n\n{str(bot_messages)}"})
    
    
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=all_messages,
            functions=functions,
            function_call= {"name": "followup"}

        )

        message = response["choices"][0]["message"]

        # Step 2, check if the model wants to call a function
        if message.get("function_call"):
            function_name = message["function_call"]["name"]
            return json.loads(message["function_call"]["arguments"])["yesno"]
        else:
            return 'error'
    except Exception as e:
        print("Error in running conversation")
        return None