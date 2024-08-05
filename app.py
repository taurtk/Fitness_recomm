import os
import requests
import streamlit as st
import matplotlib.pyplot as plt
import datetime
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Falcon API setup
AI71_BASE_URL = "https://api.ai71.ai/v1/"
AI71_API_KEY = "api71-api-971b39fd-4e72-449d-9432-42af6c76652a"

# Function to generate a chat completion
def generate_completion(messages, stream=False):
    if not AI71_API_KEY:
        st.error("API Key is missing. Please set it in the .env file.")
        return None

    headers = {
        'Authorization': f'Bearer {AI71_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "tiiuae/falcon-180b-chat",
        "messages": messages,
        "stream": stream
    }
    try:
        response = requests.post(f"{AI71_BASE_URL}chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP Error: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    return None

# Function to get meal plans and recipes
def get_meal_plan(dietary_preference):
    messages = [
        {"role": "system", "content": "You are a nutrition expert."},
        {"role": "user", "content": f"Suggest a meal plan and recipes for someone who prefers {dietary_preference} diet."}
    ]
    return generate_completion(messages)

# Function to generate workout plan
def get_workout_plan(goal):
    messages = [
        {"role": "system", "content": "You are a fitness expert."},
        {"role": "user", "content": f"Create a workout plan for someone with the goal: {goal}"}
    ]
    return generate_completion(messages)

# Initialize session state
if 'habits' not in st.session_state:
    st.session_state['habits'] = {}

if 'points' not in st.session_state:
    st.session_state['points'] = 0

# Function to add a new habit
def add_habit(habit_name):
    st.session_state['habits'][habit_name] = {
        'start_date': datetime.date.today().strftime("%Y-%m-%d"),
        'progress': []
    }

# Function to update habit progress
def update_habit(habit_name):
    st.session_state['habits'][habit_name]['progress'].append(datetime.date.today().strftime("%Y-%m-%d"))
    st.session_state['points'] += 10  # Reward points for habit completion

# Function to log nutrition
def log_nutrition(meal_description):
    st.session_state['points'] += 5  # Reward points for logging nutrition

# Define the Streamlit app
def main():
    st.title("Virtual Health Coach")
    st.write("Welcome! This virtual health coach will help you maintain healthy habits through personalized recommendations and motivational support.")

    # User input for health information
    user_info = st.text_input("Enter your health and fitness goals", "")
    dietary_preference = st.text_input("Enter your dietary preference (e.g., vegan, keto, etc.)", "")

    # Display current points
    st.sidebar.subheader("Your Points")
    st.sidebar.write(f"Points: {st.session_state['points']}")

    if user_info:
        # Query Falcon model for recommendations
        with st.spinner('Generating personalized recommendations...'):
            response = generate_completion([
                {"role": "system", "content": "You are a helpful health and fitness coach."},
                {"role": "user", "content": f"Give me health and fitness recommendations based on the following information: {user_info}"}
            ])
            if response and 'choices' in response and len(response['choices']) > 0:
                st.subheader("Your personalized recommendations:")
                st.write(response['choices'][0]['message']['content'])
            else:
                st.error("No recommendations found or API response is invalid. Please try again.")

        # Generate workout plan
        with st.spinner('Generating personalized workout plan...'):
            workout_response = get_workout_plan(user_info)
            if workout_response and 'choices' in workout_response and len(workout_response['choices']) > 0:
                st.subheader("Your personalized workout plan:")
                st.write(workout_response['choices'][0]['message']['content'])
            else:
                st.error("No workout plan found or API response is invalid. Please try again.")

    if dietary_preference:
        # Query Falcon model for meal plans and recipes
        with st.spinner('Generating meal plans and recipes...'):
            meal_plan_response = get_meal_plan(dietary_preference)
            if meal_plan_response and 'choices' in meal_plan_response and len(meal_plan_response['choices']) > 0:
                st.subheader("Your meal plan and recipes:")
                st.write(meal_plan_response['choices'][0]['message']['content'])
            else:
                st.error("No meal plans found or API response is invalid. Please try again.")

    # Nutrition logging
    st.subheader("Log Your Nutrition")
    meal_description = st.text_area("Describe your meal", "")
    if st.button("Log Meal"):
        log_nutrition(meal_description)
        st.success("Meal logged successfully! Points added.")

    # Progress tracking
    st.subheader("Track your progress")
    exercise_done = st.checkbox("I have completed my exercise today")
    if exercise_done:
        st.write("Great job! Keep it up!")
        st.session_state['points'] += 10  # Reward points for exercise completion

    # Motivational support
    st.subheader("Motivational Support")
    if st.button("Give me some motivation!"):
        motivation_response = generate_completion([
            {"role": "system", "content": "You are a helpful and motivational coach."},
            {"role": "user", "content": "Give me a motivational quote to keep me going."}
        ])
        if motivation_response and 'choices' in motivation_response and len(motivation_response['choices']) > 0:
            st.write(motivation_response['choices'][0]['message']['content'])
        else:
            st.error("No motivational quote found or API response is invalid. Please try again.")

    # Habit tracking section
    st.subheader("Habit Tracking")
    new_habit = st.text_input("Enter a new habit to track", "")
    if st.button("Add Habit"):
        add_habit(new_habit)

    for habit in st.session_state['habits'].keys():
        st.write(f"Habit: {habit}")
        if st.button(f"Mark {habit} as completed today"):
            update_habit(habit)
        st.write(f"Progress: {st.session_state['habits'][habit]['progress']}")

if __name__ == "__main__":
    main()
