from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
import os


@CrewBase
class CrewaiQuickstartCrew():
    """CrewaiQuickstart crew"""

    def __init__(self):
        super().__init__()
        self.llm = LLM(
            model=f"ollama/{os.getenv('OLLAMA_MODEL', 'llama3.2')}", 
            base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        )

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            verbose=True,
            llm=self.llm
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'],
            verbose=True,
            llm=self.llm
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CrewaiQuickstart crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )