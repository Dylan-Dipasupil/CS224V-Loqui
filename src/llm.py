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
        

# Define strategies
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
        example="I value our friendship and want to ensure we keep supporting each other through this."
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
        example="I understand your perspective now, so, I'm okay with trying your approach first, and we can reassess if needed."
    ),
    "Facts": Strategy(
        name="Facts",
        category="Neutral",
        definition="Sharing information on the context or history of the issue, including requests for clarification or summaries.",
        example="We haven't talked about it for a while, so I did not know how you were feeling. What's your current perspective?"
    ),
    "Procedural": Strategy(
        name="Procedural",
        category="Neutral",
        definition="Messages to open the discussion, including setting a comfortable tone and bringing up relevant topics.",
        example="Hey, are you free to talk?"
    ),
    "Power": Strategy(
        name="Power",
        category="Competitive",
        definition="Using threats or coercion to push the conversation toward a particular outcome.",
        example="I'm breaking up with you if you keep hanging out with him."
    ),
    "Rights": Strategy(
        name="Rights",
        category="Competitive",
        definition="Appealing to unchangeable principles or standards to direct the resolution.",
        example="I have a right to feel respected, so I need you to stop talking to me like that."
    )
}


class ChatClient:
    # 	old: meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
    def __init__(self, model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"):
        self.client = Together()
        self.model = model
        self.agent_type = ""  # One of: Cooperative, Neutral, Competitive
        self.agent_desc = "person"  # eg "romantic partner of 3 years" or "friend who wants to be more"
        self.situation = ""  # eg "Setting a boundary on spending too much time together"
        self.relationship_context = ""  # user description of person (eg 14 years old)

        self.agent_context = "" # concise string fed to agent to give it context for who it is role-playing as 
        self.base_agent_desc = ""
        self.res_score = 1  # how resolved the convo is, 1=unresolved, 5=resolved, starts as 1 bc convo is supposed to be about conflict resolution, so starts w conflict

        self.res_score_defs = {
            1: "Conflict is escalating; communication is unproductive and contentious. Both parties are in full disagreement",
            2: "Conflict is still contentious; some effort toward resolution or understanding is evident, but tension still exists.",
            3: "Conflict is not escalating but people are also not actively resolving the issue.",
            4: "Conflict is de-escalating; cooperative strategies are being employed, people are working with each other",
            5: "Conversation is de-escalated; communication is productive, cooperative, and resolution-focused. People are happy."
        }

        self.res_score_strats = {
            1: ["Power", "Rights"],
            2: ["Rights", "Facts", "Procedural"],
            3: ["Facts", "Procedural"],
            4: ["Interests", "Positive Expectations", "Proposal", "Concession"],
            5: ["Interests", "Positive Expectations", "Proposal", "Concession"]
        }


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
            full_resp = ""
            for chunk in response:
                chunk_str = chunk.choices[0].delta.content or ""
                print(chunk_str, end="", flush=True)
                full_resp += chunk_str

            return full_resp
        
        # return entire response as one
        else:
            if hasattr(response, 'choices') and response.choices:
                return response.choices[0].message.content.strip('"')
            else:
                return "Error in generating or saving response"
            

    def classify_strategy(self, user_input):
        """
        Use LLM to classify the strategy of a given user input.
        
        :param user_input: str, The user's message to be classified.
        :return: str, The identified strategy.
        """
        strategies_description = []
        for strategy_name, strategy in strategies.items():
            strategies_description.append(
                f"{strategy.category} ({strategy_name}): {strategy.definition}"
            )
        strategies_text = "\n".join(strategies_description)
        prompt = (
        f"Based on the following strategies, identify the single most relevant strategy for the given message. "
        f"Only respond with the name of the strategy, without any additional text or formatting.\n"
        f"{strategies_text}\n\n"
        f"The message is: \"{user_input}\"\n\n"
        f"Respond with only the strategy name."
    )
        strategy = self.basic_prompt(prompt, stream=False).strip()
        if "(" in strategy:
            strategy = strategy.split("(")[1].strip(")") 
        if strategy not in strategies:
            print(f"Warning: LLM returned unrecognized strategy '{strategy}'")
            
        return strategy

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
        Sets the situation variable

        :param situation: str, The situation description, eg "Setting a boundary about spending too much time together"
        """
        self.situation = situation
        
    def set_relationship_context(self, context):
        """
        Sets the relationship context variable

        :param context: str, Describes the user's relationship context
        """
        self.relationship_context = context

    def get_res_score(self):
        return self.res_score
    
    def set_base_agent_desc(self):
        """
        Creates a role description that the bot should adhere to
        """
        desc_summary_prompt = f"You are describing me. From your perspective, the conflict you have with me is \"{self.situation}\" (mentions of \"she\" or \"he\" likely refer to me). I am a {self.agent_desc} to you. You describe me as: \"{self.relationship_context}\". Based on this, describe me in the context of our conversation. Include details about how I would talk, my demeanor, my values, and my goals. Write the description in 2nd person, using 2 short sentences." 

        # calls llm and sets base_agent_desc var as response
        self.base_agent_desc = self.basic_prompt(desc_summary_prompt, stream=False)
        print(f"agent description: {self.base_agent_desc}") 

    def set_agent_context(self, strategy):
        """
        Sets the relationship context variable

        :param strategy: str, the chosen strategy that the bot should use
        """
        # build agent context using base agent description + info about current strategy that they should be using
        self.agent_context = (
            f"Respond like you are my {self.agent_desc}. {self.base_agent_desc} Respond using the {strategy} strategy. This strategy is defined as \"{strategies[strategy].definition}\" An example of a response using this strategy is \"{strategies[strategy].example}\" Respond to the other person in the first person and keep the response short and sweet as if over text message."
        )

    def format_messages(self, chat_log, user_utt):
        """
        Converts chat log from human-readable format to model-formatted input, including the model context and latest user utterance (which the bot is creating a reponse to)
        
        :param chat_log: list, the current chat log from chat_flow.py
        """
        # Initialize a list to store messages in the desired format
        formatted_messages = []        
        
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

        return formatted_messages
    
    def score_resolution(self, formatted_chat_log):
        """
        Scores the current conversation on a scale of 1-5 from unresolved to resolved
        
        :param formatted_chat_log: list of dicts, the current chat log from chat_flow.py, formatted through format_messages()
        """
        # replace original system role to make bot return a resolution score of the current conversation instead
        messages = formatted_chat_log[:]
        system_role = f"On a scale of 1-5, asssess how resolved the conflict is in this conversation. Choose the number that best describes the current state of the converation: {self.res_score_defs} \n\n Only output the number 1, 2, 3, 4, or 5. Do not output anything else."
        # append system message at the end for best role adherance (https://community.openai.com/t/the-system-role-how-it-influences-the-chat-behavior/87353)
        messages.append({"role": "system", "content": system_role})

        # call model to assses how resolved the conversation is
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
        )

        # if llm response was successful, update resolution score, otherwise it stays the same as past turn
        if hasattr(response, 'choices') and response.choices:
            stripped_resp = response.choices[0].message.content.strip('"')
            # find first digit in response, in case llm decides to not listen
            for char in stripped_resp:
                if char.isdigit():
                    self.res_score = int(char)

        print(f"Current resolution score: {self.res_score}") # TODO delete

    def choose_strategy(self):
        """
        Chooses a strategy based on the current resolution score and the agent type
        """
        if self.agent_type == "Competitive":
            # make agent try to push score down, clip at min of 1
            rscore = self.res_score - 1 if self.res_score > 1 else 1
        elif self.agent_type == "Cooperative":
            # make agent try to push score up, clip at max of 5
            rscore = self.res_score + 1 if self.res_score < 5 else 5
        else: # for Neutral agent
            # agent matches current score
            rscore = self.res_score  
        
        return random.choice(self.res_score_strats[rscore])
        

    def get_response(self, user_utt, chat_log, stream=False):
        """
        Responds to a user utterance during a simulated dialogue.
        
        :param user_utt: str, The user utterance
        :param chat_log: list, all utterances thus far (not including most recent user_utt)
        """
        try:
            # include chat log in model call if there is a chat log
            if chat_log:
                # Construct the conversation context from the history
                messages = self.format_messages(chat_log, user_utt)

                # score the current resolution of the conversation, stored as self.res_score - note: slows program more and more as convo goes on
                self.score_resolution(messages)

                # choose a random strategy based on agent type and res_score
                strategy = self.choose_strategy()
                print(f"Bot's strategy: {strategy}") # TODO delete

                # tell the agent who they are and which strategy they should be using
                self.set_agent_context(strategy)

                # append updated agent context before chat log
                messages.insert(0, {"role": "system", "content": self.agent_context})

                # call model to respond, with context for who the agent is and the conversation thus far
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=stream,
                )

            # if no chat log yet (eg first utterance), don't include in model call
            else:
                # choose a random strategy based on agent type and res_score
                strategy = self.choose_strategy()
                print(f"Bot's strategy: {strategy}") # TODO delete

                # tell the agent who they are and which strategy they should be using
                self.set_agent_context(strategy)

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

    def get_feedback(self, stats_report):
        """
        Gives natural-language feedback based on the stats report of the user's utterances so far
        
        :param stats_report: list of strings describing statistics for how often the user uses each strategy
        """
        stats_report_str = "\n".join(stats_report)

        # TODO integrate more specific feedback like offering alternatives to "bad" utterances
        # TODO shorten prompt? 
        prompt = f"""You are evaluating how well a user is doing in a difficult conversation involving {self.situation}. 
        
        The other person is the user's {self.agent_desc}. The other person is described as: '{self.relationship_context}. 
        
        Give the user constructive feedback on what they've been doing well, and what they should improve on. 
        
        Below are the descriptions and examples for each strategy, and statistics for how often the user uses each strategy. Note: it is more productive to use cooperative or neutral strategies.
        
        {strategies}

        {stats_report_str}"""

        natural_feedback = self.basic_prompt(prompt)

        return natural_feedback
