from typing import Dict, List
from autogen import ConversableAgent
import sys
import os
import math
import math


def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    """
    This function takes in a restaurant name and
    returns the reviews for that restaurant.
    The output should be a dictionary with the key being the restaurant name
    and the value being a list of reviews for that restaurant.
    The "data fetch agent" should have access to this function signature,
    and it should be able to suggest this as a function call.
    Example:
    > fetch_restaurant_data("Applebee's")
    {"Applebee's": ["The food at Applebee's was average,
    with nothing particularly standing out.", ...]}
    """
    reviews = []
    prefix_length = len(restaurant_name) + 2  # +2 for the dot and space
    with open("restaurant-data.txt", "r") as file:
        for line in file:
            restaurant_in_line = line[:prefix_length-2]
            if restaurant_name.lower() == restaurant_in_line.lower():
                reviews.append(line[prefix_length:-1])
    if len(reviews) == 0:
        raise Exception(f"""No reviews found for restaurant: {restaurant_name}.
                        Make sure the restaurant name is correct.""")
    return {restaurant_name: reviews}


def calculate_overall_score(restaurant_name: str, food_scores: List[int],
                            customer_service_scores: List[int]) -> Dict[str, str]:
    """
    This function takes in a restaurant name, a list of food scores from 1-5,
    and a list of customer service scores from 1-5
    The output should be a score between 0 and 10, which is computed as the following:
    SUM(sqrt(food_scores[i]**2 * customer_service_scores[i]) * 1/(N * sqrt(125)) * 10
    The above formula is a geometric mean of the scores,
    which penalizes food quality more than customer service.
    Example:
    > calculate_overall_score("Applebee's", [1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    {"Applebee's": 5.048}
    """
    if len(food_scores) != len(customer_service_scores):
        raise ValueError("Food scores and service scores must have the same length")

    if not all(1 <= score <= 5 for score in food_scores + customer_service_scores):
        raise ValueError("All scores must be between 1 and 5")

    N = len(food_scores)
    total = 0

    for food, service in zip(food_scores, customer_service_scores):
        total += math.sqrt(food**2 * service) * (1 / (N * math.sqrt(125)))
    
    # Calculate final score using the formula
    # SUM(sqrt(food_scores[i]**2 * customer_service_scores[i]) * 1/(N * sqrt(125)) * 10
    final_score = total * 10
    return {restaurant_name:  f"{final_score:.3f}"}


def get_data_fetch_agent_prompt() -> str:
    return """
    You return restaurant data for a specific restaurant with the `fetch_restaurant_data` tool.
    """


def get_review_analysis_agent_prompt() -> str:
    return """
    You are a restaurant expert evaluating restaurant reviews.  You should extract two scores from each review:

    1. `food_score`: the quality of food at the restaurant. This will be a score from 1-5.
    2. `customer_service_score`: the quality of customer service at the restaurant. This will be a score from 1-5.
    You should extract these two scores by looking for keywords in the review.
    Each review has keyword adjectives that correspond to the score that the restaurant should get
    for its `food_score` and `customer_service_score`. Here are the keywords you should look out for:
    - Score 1 has one of these adjectives: awful, horrible, or disgusting.
    - Score 2 has one of these adjectives: bad, unpleasant, or offensive.
    - Score 3 has one of these adjectives: average, uninspiring, or forgettable.
    - Score 4 has one of these adjectives: good, enjoyable, or satisfying.
    - Score 5 has one of these adjectives: awesome, incredible, or amazing.
    Each review will have exactly only two of these keywords (adjective describing food and adjective describing customer service),
    and the score is only determined through the above listed keywords. No other factors go into score extraction.
    To accomplish this, make sure to extract the relevant keywords associated with both food and customer service and only then create the scores.
    """


def get_scoring_agent_prompt() -> str:
    return """
    You are responsible for identifying the correct lists of food scores and customer service scores to use in `calculate_overall_score` function.
    ALL restaurant scoring or evaluation have to be done through running `calculate_overall_score`.
    """


# Do not modify the signature of the "main" function.
def main(user_query: str):
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}

    entrypoint_agent_system_message = """You are a data analyst who is tasked with analyzing restaurant reviews and executing tasks requested of you. When you are done, reply DONE. """

    # Entrypoint/supervisor agent
    entrypoint_agent = ConversableAgent("entrypoint_agent",
                                        system_message=entrypoint_agent_system_message,
                                        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("DONE"),
                                        llm_config=llm_config)
    # `register_for_llm` agent can call the tool - ask to execute?
    entrypoint_agent.register_for_llm(name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    entrypoint_agent.register_for_llm(name="calculate_overall_score", description="Calculates the overall restaurant score given the restaurant name, a list of food scores, and a list of customer service scores.")(calculate_overall_score)

    # Data fetch agent
    data_fetch_agent = ConversableAgent(
                                        "data_fetch_agent",
                                        system_message=get_data_fetch_agent_prompt(),
                                        llm_config=llm_config
                                        )
    # `register_for_execution` can execute the tool’s function.
    data_fetch_agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)
    
    # Review agent
    review_analysis_agent = ConversableAgent(
                                            "review_analysis_agent",
                                            system_message=get_review_analysis_agent_prompt(),
                                            llm_config=llm_config
                                            )
    # Scoring agent
    scoring_agent = ConversableAgent(
                                    "scoring_agent",
                                    system_message=get_scoring_agent_prompt(),
                                    llm_config=llm_config,
                                    )
    scoring_agent.register_for_execution(name="calculate_overall_score")(calculate_overall_score)
    
    data_fetch_task = f""" The client asked {user_query}. 
    The task is to fetch restaurant data and return all the reviews for the restaurant in an enumerated list. 
    Make sure you fix the restaurant name if there are any spelling erros. DO NOT ADD ANY extra words.
    Keep trying until you find the reviews."""
 
    entrypoint_agent.initiate_chats(
    [
        {
            "recipient": data_fetch_agent,
            "message": data_fetch_task,
            "max_turns": 2,
            "summary_method": "last_msg"
        },
        {
            "recipient": review_analysis_agent,
            "message": "Analyse each review from the list individually",
            "max_turns": 1,
            "summary_method": "last_msg",
        },
        {
            "recipient": scoring_agent,
            "message": f"Build the correct lists of `food_scores` and `customer_service_scores` from the reviews. Use the `calculate_overall_score` tool.",
            "max_turns": 3,
            "summary_method": "reflection_with_llm",
            "summary_prompt": f"Answer the customer query: {user_query}."
        },
    ]
)


# DO NOT modify this code below.
if __name__ == "__main__":
    assert len(sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
    main(sys.argv[1])
