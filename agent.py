from tools import scrape_tool, search_tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-5.4-mini-2026-03-17", temperature=0)
parser = StrOutputParser()

def get_search_agent():
    return create_agent(
        model = llm,
        system_prompt="Using the tool in mendatory, Always provide results in format,\nTitle:...\nURL:...\nContent:...",
        tools = [search_tool]
    )


def get_reader_agent():
    return create_agent(
        model = llm,
        system_prompt="Using the tool is mendatory",
        tools = [scrape_tool]
    )


writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional.
-Max 1500 words.
-this is the written report: {report} and Feedback on written report: {feedback}, if report or feedback==None ignore it and write report, else make the improvements which can be made, without voilating upper instructions.""")
])

writer_chain = writer_prompt | llm | parser


critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...""")
])

critic_chain = critic_prompt | llm | parser