#!/usr/bin/env python
import sys
from dotenv import load_dotenv

from crewai_quickstart.crew import CrewaiQuickstartCrew


def run():
    """
    Run the crew.
    """
    load_dotenv()
    
    inputs = {
        'topic': 'AI LLMs'
    }
    
    if len(sys.argv) > 1:
        inputs['topic'] = ' '.join(sys.argv[1:])
    
    print(f"Running crew with topic: {inputs['topic']}")
    CrewaiQuickstartCrew().crew().kickoff(inputs=inputs)


if __name__ == "__main__":
    run()