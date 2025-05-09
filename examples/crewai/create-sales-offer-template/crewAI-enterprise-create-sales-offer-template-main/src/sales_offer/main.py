#!/usr/bin/env python
import sys

from sales_offer.crew import SalesOfferCrew

# This main file is intended to be a way for your to run your
# crew locally, so refrain from adding necessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


def run():
    """Run the crew."""
    inputs = {
        "customer_info": {
            "name": "Placeholder Company",
            "industry": "Placeholder Industry",
            "size": "Placeholder Size",
            "current_challenges": "Placeholder Challenges",
            "budget_range": "Placeholder Budget",
        },
        "company_info": {
            "name": "Placeholder Company",
            "products": ["Placeholder Product 1", "Placeholder Product 2"],
            "pricing_models": [
                "Placeholder Pricing Model 1",
                "Placeholder Pricing Model 2",
            ],
            "unique_selling_points": ["Placeholder USP 1", "Placeholder USP 2"],
        },
    }
    SalesOfferCrew().crew().kickoff(inputs=inputs)


def train():
    """Train the crew for a given number of iterations."""
    inputs = {"topic": "AI LLMs"}
    try:
        SalesOfferCrew().crew().train(
            n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """Replay the crew execution from a specific task."""
    try:
        SalesOfferCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """Test the crew execution and returns the results."""
    inputs = {"topic": "AI LLMs"}
    try:
        SalesOfferCrew().crew().test(
            n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
