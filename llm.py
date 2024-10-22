# export TOGETHER_API_KEY=a235d8aef8b2bb116dea5adda07245a7d0852a8cd64e3b6d4dcd56b250d4fc01
import os
from together import Together
import random

categories = {"Cooperative": ["interests", "positive expectations", "proposal", "concession"], 
                           "Neutral": ["facts", "procedural"],
                           "Competitive": ["Power", "Rights"]}

class Strategy:
    def __init__(self, name, category, definition, example):
        self.name = name
        self.category = category
        self.definition = definition
        self.example = example

# Define strategies TODO make more relationship-oriented
strategies = {
    "Interests": Strategy(
        name="Interests",
        category="Cooperative",
        definition="Reference to the wants, needs, or concerns of one or both parties. This may include questions about why the negotiator wants or feels the way they do.",
        example="We can figure this out - I understand that you\'ve been really busy lately."
    ),
    "Positive Expectations": Strategy(
        name="Positive Expectations",
        category="Cooperative",
        definition="Communicating positive expectations through the recognition of similarities and common goals.",
        example="I know you\'re an excellent employee and I want to make sure you get a promotion."
    ),
    "Proposal": Strategy(
        name="Proposal",
        category="Cooperative",
        definition="Proposing concrete recommendations that may help resolve the conflict.",
        example="Why don\'t we record your progress weekly instead of monthly, so we can stay on track?"
    ),
    "Concession": Strategy(
        name="Concession",
        category="Cooperative",
        definition="Changing an initial view or position (in response to a proposal) to resolve a conflict.",
        example="That makes sense - I\'ll try recording my weekly progress instead of doing it monthly."
    ),
    "Facts": Strategy(
        name="Facts",
        category="Neutral",
        definition="Providing information on the situation or history of the dispute, including requests for information, clarification, or summaries.",
        example="Unfortunately, I haven\'t been able to keep track of your progress over the last several weeks."
    ),
    "Procedural": Strategy(
        name="Procedural",
        category="Neutral",
        definition="Introductory messages, including discussion about discussion topics, procedures, etc.",
        example="Hi! How are you? Do you have time today to talk about a promotion?"
    ),
    "Power": Strategy(
        name="Power",
        category="Competitive",
        definition="Using threats and coercion to try to force the conversation into a resolution.",
        example="I\'m going to tell everyone you\'ve been missing deadlines."
    ),
    "Rights": Strategy(
        name="Rights",
        category="Competitive",
        definition="Appealing to fixed norms and standards to guide a resolution.",
        example="Sorry, I can\'t do anything - company policy doesn\'t allow that."
    )
}


class ChatClient:
    def __init__(self, model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"):
        self.client = Together()
        self.model = model
        self.agent_type = ""  # One of: Cooperative, Neutral, Competitive
        self.agent_desc = "person"  # eg "romantic partner of 3 years" or "friend who wants to be more"
        self.situation = ""  # eg "Setting a boundary on spending too much time together"

    def basic_prompt(self, prompt, stream=True):
        """
        Sends a prompt to the chat model and returns the response.

        :param prompt: str, The prompt to send to the model.
        :param stream: bool, Whether to stream (print out word chunks as they come, like chatGPT does where it looks like it's typing) the response or not (default is True).
        """
        # call model
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=stream,
        )
        
        # print out word chunks as they come
        if stream:
            for chunk in stream:
                print(chunk.choices[0].delta.content or "", end="", flush=True)
        # print out the whole response together
        else:
            response = stream.read()
            return response
    

    def set_agent_type(self, type):
        """
        Sets the agent_type variable

        :param type: str, The agent type. One of: Cooperative, Neutral, Competitive
        """
        # check validity
        if type in ["Cooperative", "Neutral", "Competitive"]:
            # set var
            self.agent_type = type
        else:
            raise Exception("Not a valid agent type. Must be one of: Cooperative, Neutral, Competitive")
        

    def set_agent_desc(self, desc):
        """
        Sets the agent_desc variable

        :param desc: str, The agent description, eg "romantic partner of 3 years" or "friend who wants to be more"
        """
        self.agent_desc = desc

    
    def set_situation(self, situation):
        """
        Sets the agent_desc variable

        :param situation: str, The situation description, eg "Setting a boundary about spending too much time together"
        """
        self.situation = situation
        

    def get_response(self, user_utt):
        """
        Responds to a user utterance during a simulated dialogue. Assumes each API call is independent and there is no "conversation" feature, TODO see if this is the case

        :param user_utt: str, The user utterance
        """
        # choose a random strategy based on agent type
        strategy = random.choice(categories[self.agent_type])

        # build prompt
        prompt = f"You are a {self.agent_type} {self.agent_desc} trying to get through a conflict involving {self.situation}. Your partner just said \"{user_utt}\". Formulate a response using the {strategy} strategy. This strategy is defined as {strategies[strategy].definition}. An example of a response using this strategy is \"{strategies[strategy].example}\"."

        # prompt API
        response = self.basic_prompt(prompt)

        return response

'''
Basic Usage Example:

chat_client = ChatClient()
chat_client.basic_prompt("What are some fun things to do in New York?")
'''
