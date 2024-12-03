# Restaurant Review Analysis with AutoGen Framework

## Overview

This project uses the **AutoGen Framework** and **LLMs** to analyze unstructured restaurant reviews. The goal is to provide scores for food quality and customer service based on keywords in reviews and calculate an overall score for a given restaurant. More information in Instructions.md.
This is a solution to lab01 from the [LLM Agents MOOC](https://llmagents-learning.org/f24)

---

## How It Works

1. **Fetch Restaurant Data**:
 - The `fetch_restaurant_data` function retrieves all reviews for the queried restaurant from `restaurant-data.txt`.
 
2. **Analyze Reviews**:
 - The `review_analysis_agent` identifies keywords to generate `food_score` and `customer_service_score` for each review.

3. **Compute Overall Score**:
 - The `scoring_agent` aggregates scores using the `calculate_overall_score` function to generate a final rating.

4. **User Query**:
 - Accepts natural language queries like:
   - *"How good is McDonald's as a restaurant?"*
   - *"What would you rate Starbucks?"*

---

## Setup and Installation

1. **Clone the Repository**:
 ```bash
 git clone <repository_url>
 cd <repository_name>
 ```

2. **Create and Activate a Virtual Environment**:
 ```bash
python3 -m venv env
source env/bin/activate  # For macOS/Linux
.\env\Scripts\activate   # For Windows
  ```

3. **Install Dependencies**:
 ```bash
pip install -r requirements.txt
  ```

4. **Set Up OpenAI API Key**:
- Create an OpenAI API key [here](https://platform.openai.com/docs/quickstart).
- Store it as an environment variable

 ```bash
export OPENAI_API_KEY=your_api_key  # For macOS/Linux
set OPENAI_API_KEY=your_api_key    # For Windows
  ```
---

## Running the Project

1. **Run the Main Script**:
 ```bash
python main.py "<your_query>"
  ```

Example:
 ```bash
python main.py "How good is Subway as a restaurant?"
  ```

2. **Run Tests**:
 ```bash
python test.py
  ```

---

##   File Structure

- main.py: Main implementation of the solution.
- test.py: Public tests for verifying the solution.
- restaurant-data.txt: Dataset containing restaurant reviews.
- requirements.txt: List of required Python packages.
- Instructions.md: Lab instructions and guidelines.