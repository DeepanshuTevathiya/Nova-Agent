# ✦ Nova — Deep Research Agent

Nova is a multi-agent research pipeline: give it a topic, and it searches the live web,
reads the most relevant source in depth, drafts a report, critiques its own draft, and
rewrites it into a polished final version — all automatically, with a vibrant one-page
Streamlit UI on top.

## How it works

Nova runs a 5-step agent pipeline for every query:

1. **🔎 Search** — a search agent scans the web for recent, reliable sources on the topic.
2. **📖 Read** — a reader agent picks the most promising URL from the search results and
   scrapes it for deeper content.
3. **✍️ Draft** — a writer chain combines the search results and scraped content into a
   first-draft report.
4. **🧠 Critique** — a critic chain reviews the draft and lists concrete improvements.
5. **✨ Finalize** — the writer chain rewrites the draft using its own critique into the
   final report.

Each step's output (search results, scraped content, draft, critique, final report) is
kept and shown separately in the UI, not just the end result.

## Project structure

```
DEEP_RESEARCH_AGENT/
├── agent.py          # agent/chain definitions: get_search_agent, get_reader_agent,
│                      # writer_chain, critic_chain
├── tools.py           # tools used by the agents (e.g. web search, scraping)
├── pipeline.py         # research_pipeline(topic) — runs the 5-step pipeline end to end,
│                      # can also be run standalone from the command line
├── app.py              # Streamlit UI ("Nova") — single-page, vibrant, animated front end
├── requirements.txt     # Python dependencies
└── .env                # API keys / environment variables (not committed)
```

## Setup

1. **Clone the project and create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Create a `.env` file in the project root with the API keys your `agent.py` / `tools.py`
   rely on (for example, an LLM provider key and a search API key). Check those two files
   for the exact variable names they expect.

## Running it

**Command line** (runs the pipeline once and prints each step to the terminal):
```bash
python pipeline.py
```

**Streamlit UI** (recommended):
```bash
streamlit run app.py
```
Then open the local URL Streamlit prints (usually `http://localhost:8501`), type a topic
into the search bar, and hit **Research**.

## UI features

- Single-page layout — header, animated hero with a live search bar, "how it works" step
  cards, results section, and footer.
- Live progress updates while the agents work (search → read → draft → critique → finalize).
- Tabbed results: **Final Report**, **Draft**, **Critique**, and **Raw Research**
  (search results + scraped content).
- Download the final report as a `.md` file.
- Recent topics shown as clickable chips so you can revisit a past run without re-querying.

## Notes

- The pipeline can take anywhere from under a minute to a few minutes per topic, depending
  on the LLM and search/scrape latency.
- If a step fails (e.g. a scrape error or a rate-limited API), the UI surfaces the error
  instead of crashing, so you can retry.

## License

Add your preferred license here (e.g. MIT).
