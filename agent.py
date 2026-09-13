from tools import scrape_tool, search_tool
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.4, max_tokens=1200)
# llm = init_chat_model(model="openai/gpt-oss-20b", model_provider="groq")
parser = StrOutputParser()

# class searchResultformat(BaseModel):
#     Title:str = Field(description="Title of the search result.")
#     Url:List[str] = Field(description="Urls that contain the info about asked query.")
#     Content:str = Field(description="Content about the query.")

def get_search_agent(llm=llm):
    return create_agent(
        model=llm,
        system_prompt=(
            "Use the search tool. Always provide results in this format:\n"
            "Title: ...\nURL: ...\nContent: ..."
        ),
        tools=[search_tool],
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