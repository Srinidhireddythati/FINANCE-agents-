import streamlit as st
from finance.openai_model import OpenAIModel
from finance.agents import Agent
from finance.tasks import Task
from finance.pipeline import LinearSyncPipeline
from duckduckgo_search import DDGS


# Set up the Streamlit app
st.title("AI Personal Finance Planner 💰")
st.caption("Manage your finances with AI Personal Finance Manager by creating personalized budgets, investment plans, and savings strategies using GPT-4")

# Get OpenAI API key from user
openai_api_key = st.text_input("Enter OpenAI API Key to access GPT-4", type="password")

if openai_api_key:
    openai_model = OpenAIModel(
        api_key=openai_api_key,
        parameters={
            "model": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": 1500,
        },
    )

    # Define agents
    search_terms_agent = Agent(
        role="Financial Researcher",
        prompt_persona="You are a world-class financial researcher. Given a user's financial goals and current financial situation, generate a list of 3 search terms for finding relevant financial advice, investment opportunities, and savings strategies."
    )

    financial_plan_agent = Agent(
        role="Senior Financial Planner",
        prompt_persona="You are a senior financial planner. Given a user's financial goals, current financial situation, and a list of research results, your goal is to generate a personalized financial plan that includes suggested budgets, investment plans, and savings strategies."
    )

    # Define tasks
    get_search_terms_task = Task(
        name="Generate Search Terms",
        model=openai_model,
        instructions="Given a user's financial goals and current financial situation, generate a list of 3 search terms for finding relevant financial advice, investment opportunities, and savings strategies.",
        agent=search_terms_agent,
    )

    get_search_results_task = Task(
        name="Get Search Results",
        model=openai_model,
        instructions="Use the search terms provided to find relevant financial advice, investment opportunities, and savings strategies.",
        agent=None,  # This task will handle search results directly
    )

    get_financial_plan_task = Task(
        name="Generate Financial Plan",
        model=openai_model,
        instructions="Given a user's financial goals, current financial situation, and a list of research results, generate a personalized financial plan that includes suggested budgets, investment plans, and savings strategies.",
        agent=financial_plan_agent,
    )

    # Input fields for the user's financial goals and current financial situation
    financial_goals = st.text_input("What are your financial goals?")
    current_situation = st.text_area("Describe your current financial situation")

    if st.button("Generate Financial Plan"):
        with st.spinner("Processing..."):
            # Generate search terms
            search_terms_task = get_search_terms_task.execute()
            search_terms = search_terms_task['task_output'].split('\n')
            
            # Debug: Print search terms
            print("Search Terms:", search_terms)
            st.write("Search Terms:", search_terms)

            if search_terms:
                # Get search results
                ddgs = DDGS()
                search_results = []
                for term in search_terms:
                    if term.strip():  # Ensure term is not empty
                        results = ddgs.text(term.strip(), max_results=3)
                        for result in results:
                            search_results.append(result['title'] + ": " + result['href'])
                search_results_text = "\n".join(search_results)

                # Debug: Print search results
                print("Search Results:", search_results_text)
                st.write("Search Results:", search_results_text)

                # Generate financial plan
                get_financial_plan_task.instructions = f"Given a user's financial goals, current financial situation, and a list of research results, generate a personalized financial plan that includes suggested budgets, investment plans, and savings strategies.\n\nUser's financial goals: {financial_goals}\nUser's current financial situation: {current_situation}\nResearch results: {search_results_text}"
                financial_plan_task = get_financial_plan_task.execute()
                response = financial_plan_task['task_output']
                st.write(response)
            else:
                st.error("No search terms generated. Please check your input and try again.")
