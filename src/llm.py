# export TOGETHER_API_KEY=a235d8aef8b2bb116dea5adda07245a7d0852a8cd64e3b6d4dcd56b250d4fc01
import os
from together import Together
import random
import json
import difflib

categories = {
    "Cooperative": ["Interests", "Positive Expectations", "Proposal", "Concession"], 
    "Neutral": ["Facts", "Procedural"],
    "Competitive": ["Power", "Rights"]
}

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
        definition="Reference to the wants, needs, or concerns of one or both people in the relationship. This may include questions about why the person feels a certain way.",
        example="I can see this is really important to you. I'd like to understand more about why you feel this way."
    ),
    "Positive Expectations": Strategy(
        name="Positive Expectations",
        category="Cooperative",
        definition="Communicating positive expectations through the recognition of shared values and goals within the relationship.",
        example="I know you're always supportive of me, and I want to make sure I'm there for you in the same way."
    ),
    "Proposal": Strategy(
        name="Proposal",
        category="Cooperative",
        definition="Suggesting concrete ideas that may help address the issue within the relationship.",
        example="How about we check in with each other weekly instead of waiting until things build up?"
    ),
    "Concession": Strategy(
        name="Concession",
        category="Cooperative",
        definition="Adjusting an initial view or approach (in response to a suggestion) to help resolve the issue in the relationship.",
        example="I get it now - let's try checking in weekly if that works better for you."
    ),
    "Facts": Strategy(
        name="Facts",
        category="Neutral",
        definition="Sharing information on the context or history of the issue, including requests for clarification or summaries.",
        example="I didn't realize you felt this way - we haven't talked about it for a while."
    ),
    "Procedural": Strategy(
        name="Procedural",
        category="Neutral",
        definition="Introductory messages to open the discussion, including setting a comfortable tone and bringing up relevant topics.",
        example="Hey, I'd love to check in with you sometime soon. Are you free later to talk?"
    ),
    "Power": Strategy(
        name="Power",
        category="Competitive",
        definition="Using threats or coercion to push the conversation toward a particular outcome.",
        example="If you don't talk to me about this, I'm going to stop talking to you altogether."
    ),
    "Rights": Strategy(
        name="Rights",
        category="Competitive",
        definition="Appealing to unchangeable principles or standards to direct the resolution.",
        example="I can't compromise on this because it goes against what I believe in."
    )
}


class ChatClient:
    def __init__(self, model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"):
        self.client = Together()
        self.model = model
        self.agent_type = ""  # One of: Cooperative, Neutral, Competitive
        self.agent_desc = "person"  # eg "romantic partner of 3 years" or "friend who wants to be more"
        self.situation = ""  # eg "Setting a boundary on spending too much time together"
        self.relationship_context = ""  # user input about relationship
        self.agent_context = "" # concise string fed to agent to give it context for who it is role-playing as


    def basic_prompt(self, prompt, stream=True):
        """
        Sends a prompt to the chat model and returns the response.

        :param prompt: str, The prompt to send to the model.
        :param stream: bool, Whether to stream (print out word chunks as they come, like chatGPT does where it looks like it's typing) the response or not (default is True).
        """
        # call model
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=stream,
        )
        
        # print out word chunks as they come
        if stream:
            for chunk in response:
                print(chunk.choices[0].delta.content or "", end="", flush=True)
        # print out the whole response together
        else:
            if hasattr(response, 'choices') and response.choices:
                return response.choices[0].message.content.strip('"')

    def set_agent_type(self, type):
        """
        Sets the agent_type variable

        :param type: str, The agent type. One of: Cooperative, Neutral, Competitive
        """
        # check validity
        normalized_type = type.lower().capitalize()
        if normalized_type in ["Cooperative", "Neutral", "Competitive"]:
            # set var
            self.agent_type = normalized_type
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
        
    def set_relationship_context(self, context):
        """
        Sets the relationship context variable

        :param context: str, Describes the user's relationship context
        """
        self.relationship_context = context

    def set_agent_context(self, strategy):
        # build agent context
        self.agent_context = (
            f"You are a {self.agent_type} {self.agent_desc} trying to get through a conflict "
            f"involving {self.situation}. Your relationship with the user is: '{self.relationship_context}'. "
            f"Formulate a response using the {strategy} strategy. This strategy is defined as \"{strategies[strategy].definition}\" "
            f"An example of a response using this strategy is \"{strategies[strategy].example}\" "
            f"Respond in the first person and keep the response short and sweet as if over text message."
        )

    def format_messages(self, chat_log, user_utt):
        """
        Converts chat log from human-readable format to model-formatted input, including the model context and latest user utterance (which the bot is creating a reponse to)
        
        :param chat_log: list, the current chat log from chat_flow.py
        """
        # Initialize a list to store messages in the desired format
        formatted_messages = [{"role": "system", "content": self.agent_context}]

        # Process each line in the chat log
        for line in chat_log:
            line = line.strip()  # Remove any extra whitespace
            if line.startswith("You:"):
                # Extract the user's message content
                content = line.replace("You:", "", 1).strip()
                formatted_messages.append({"role": "user", "content": content})
            elif line.startswith("Bot:"):
                # Extract the bot's message content
                content = line.replace("Bot:", "", 1).strip()
                formatted_messages.append({"role": "assistant", "content": content})

        formatted_messages.append({"role": "user", "content": user_utt})

        # Convert the list to a JSON-formatted string
        #conversation = json.dumps(formatted_messages, indent=6)

        return formatted_messages

    def get_response(self, user_utt, chat_log, stream=False):
        """
        Responds to a user utterance during a simulated dialogue.
        
        :param user_utt: str, The user utterance
        """
        try:
            # choose a random strategy based on agent type
            strategy = random.choice(categories[self.agent_type])

            # instruct agent on who they are are how they should respond
            self.set_agent_context(strategy)

            # include chat log in model call if there is a chat log
            if chat_log:
                # Construct the conversation context from the history
                messages = self.format_messages(chat_log, user_utt)

                # call model to respond, with context for who the agent is and the conversation thus far
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=stream,
                )

            # if no chat log yet (eg first utterance), don't include in model call
            else:
                # call model to respond, with context for who the agent is and the most recent user utterance
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": self.agent_context},
                            {"role": "user", "content": user_utt}],
                    stream=stream,
                )
        
            # print out word chunks as they come
            if stream:
                for chunk in response:
                    print(chunk.choices[0].delta.content or "", end="", flush=True)
            # print out the whole response together
            else:
                if hasattr(response, 'choices') and response.choices:
                    return response.choices[0].message.content.strip('"')

            return response

        except Exception as e:
            print(f"An unexpected error occurred: {e}")



'''
Basic Usage Example:

chat_client = ChatClient()
chat_client.basic_prompt("What are some fun things to do in New York?")
'''
