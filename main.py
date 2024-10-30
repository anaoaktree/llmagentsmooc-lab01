from typing import Dict, List
from autogen import ConversableAgent
import sys
import os

# This gloabl dictionary will store the reviews for all restaurants in the file.
restaurant_data_dict = {}

def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    """
    This function takes in a restaurant name and returns the reviews for that restaurant. 
    The output should be a dictionary with the key being the restaurant name and the value being a list of reviews for that restaurant.
    The "data fetch agent" should have access to this function signature, and it should be able to suggest this as a function call. 
    Example:
    > fetch_restaurant_data("Applebee's")
    {"Applebee's": ["The food at Applebee's was average, with nothing particularly standing out.", ...]}
    """
    if restaurant_name in restaurant_data_dict:
        return {restaurant_name: restaurant_data_dict[restaurant_name]}
    reviews = []
    prefix_length = len(restaurant_name) + 2  # +2 for the dot and space
    with open("restaurant-data.txt", "r") as file:
        for line in file:
            if line.startswith(restaurant_name):
                reviews.append(line[prefix_length:-1])
    restaurant_data_dict[restaurant_name] = reviews
    return {restaurant_name: reviews}

def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    # TODO
    # This function takes in a restaurant name, a list of food scores from 1-5, and a list of customer service scores from 1-5
    # The output should be a score between 0 and 10, which is computed as the following:
    # SUM(sqrt(food_scores[i]**2 * customer_service_scores[i]) * 1/(N * sqrt(125)) * 10
    # The above formula is a geometric mean of the scores, which penalizes food quality more than customer service. 
    # Example:
    # > calculate_overall_score("Applebee's", [1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    # {"Applebee's": 5.048}
    # NOTE: be sure to that the score includes AT LEAST 3  decimal places. The public tests will only read scores that have 
    # at least 3 decimal places.
    pass

def get_review_analysis_agent_prompt() -> str:
    return """
    You are a restaurant expert evaluating restaurant reviews.  You should extract two scores from each review:

    1. `food_score`: the quality of food at the restaurant. This will be a score from 1-5.
    2. `customer_service_score`: the quality of customer service at the restaurant. This will be a score from 1-5. 
    You should extract these two scores by looking for keywords in the review. Each review has keyword adjectives that correspond to the score that the restaurant should get for its `food_score` and `customer_service_score`.
     Here are the keywords you should look out for:
    - Score 1 has one of these adjectives: awful, horrible, or disgusting.
    - Score 2 has one of these adjectives: bad, unpleasant, or offensive.
    - Score 3 has one of these adjectives: average, uninspiring, or forgettable.
    - Score 4 has one of these adjectives: good, enjoyable, or satisfying.
    - Score 5 has one of these adjectives: awesome, incredible, or amazing.
    Each review will have exactly only two of these keywords (adjective describing food and adjective describing customer service), and the score is only determined through the above listed keywords. No other factors go into score extraction.
    Write ```TERMINATE``` when you are done with all reviews.
    """

#    Example session:
    # 
# Query: {McDonald's:[The food at McDonald's was average, but the customer service was unpleasant. The uninspiring menu options were served quickly, but the staff seemed disinterested and unhelpful.]}
    # Answer: 1. 'average', which corresponds to a `food_score` of 3; 'unpleasant', which corresponds to a `customer_service_score` of 2.
    #     To accomplish this, you should enumerate all the reviews, make sure to extract the relevant keywords associated with both food and customer service and create the scores.
    # Do this for every review and return an enumerated list of reviews.
    # Thought: I should through each McDonald's review from the above list and assign it a score
    # Review: We see that the food is described as 'average', which corresponds to a `food_score` of 3. We also notice that the customer service is described as 'unpleasant', which corresponds to a `customer_service_score` of 2.
    # Answer: 1. 


## Main control flow
####

# Do not modify the signature of the "main" function.
def main(user_query: str):
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}

    entrypoint_agent_system_message = """You are a data analyst who is tasked with analyzing restaurant reviews and executing tasks requested of you. """

    task1=f""" The client asked {user_query}. The task is to fetch restaurant data and return all the reviews for the restaurant in an enumerated list."""
    task2="""You will receive a Python dictionary where the key is the name of the restaurants and the values are client reviews for that restaurant. Analyse each review"""
    # the main entrypoint/supervisor agent
    entrypoint_agent = ConversableAgent("entrypoint_agent", 
                                        system_message=entrypoint_agent_system_message, 
                                        llm_config=llm_config)
    # `register_for_llm` agent can call the tool - ask to execute?
    entrypoint_agent.register_for_llm(name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    # `register_for_execution` can execute the tool’s function.

    # TODO
    # Create more agents here. 
    data_fetch_agent = ConversableAgent("data_fetch_agent", 
                                        system_message="You return restaurant data for a specific restaurant with the `fetch_restaurant_data` tool.", 
                                        llm_config=llm_config)
    data_fetch_agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)
    
    review_analysis_agent = ConversableAgent("review_analysis_agent", 
                                        system_message=get_review_analysis_agent_prompt(),
                                        llm_config=llm_config)
 

    chat_results = entrypoint_agent.initiate_chats(
    [
        {
            "recipient": data_fetch_agent,
            "message": task1,
            "max_turns":2,
            "summary_method": "last_msg"
        },
        {
            "recipient": review_analysis_agent,
            "message": "Analyse each review from the list individually",
            "max_turns": 1,
            "summary_method": "last_msg",
        },
    ]
)

    # TODO
    # Fill in the argument to `initiate_chats` below, calling the correct agents sequentially.
    # If you decide to use another conversation pattern, feel free to disregard this code.
    
    # Uncomment once you initiate the chat with at least one agent.
    # result = entrypoint_agent.initiate_chats([{}])
    
# DO NOT modify this code below.
if __name__ == "__main__":
    assert len(sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
    main(sys.argv[1])


