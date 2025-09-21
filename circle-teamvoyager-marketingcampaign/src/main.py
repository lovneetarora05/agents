from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM  # ✅ CrewAI's wrapper around LiteLLM

# Point CrewAI -> LiteLLM -> Ollama
ollama_llm = LLM(
    model="ollama/llama3",                 # ✅ note the provider prefix
    base_url="http://localhost:11434",     # Ollama default
    api_key="NA"                           # Ollama doesn’t need it, but field is required
)

researcher = Agent(
    role="Researcher",
    goal="Find and summarize the latest AI news clearly for beginners.",
    backstory="You track AI news daily and explain it simply.",
    llm=ollama_llm,
)

task = Task(
    description="Summarize the top 3 AI news stories from the past 7 days.",
    expected_output="Exactly 3 bullets: headline + 2–3 sentence summary each.",
    agent=researcher,
)

crew = Crew(agents=[researcher], tasks=[task], process=Process.sequential, verbose=True)
result = crew.kickoff()  # ✅ not run()
print(result)
