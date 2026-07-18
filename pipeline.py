from agent import get_search_agent, get_reader_agent, writer_chain, critic_chain

def research_pipeline(topic: str) -> dict:

    state = {}

    # SEARCH AGENT
    print('\n'+'='*50)
    print("STEP - 1: SEARCH AGENT IS WORKING...")
    print("="*50, '\n')

    search_agent = get_search_agent()
    search_results = search_agent.invoke(
        {'messages':f"Find recent, reliable and detailed information about: {topic}"}
    )
    state['search_results'] = search_results['messages'][-1].content
    print("SEARCH RESULTS:\n",state['search_results'])


    # READER AGENT
    print('\n'+'='*50)
    print("STEP - 2: READER AGENT IS WORKING...")
    print("="*50, '\n')

    reader_agent = get_reader_agent()
    reader_results = reader_agent.invoke(
        {'messages':f"""Based on the following search results about '{topic}',
        pick the most relevant URL and scrape it for deeper content.\n\n
        Search Results: \n{state ['search_results'] [:800]}"""}
    )

    state['scraped_content'] = reader_results['messages'][-1].content
    print('\nREADER RESULTS:\n', state['scraped_content'])


    # WRITER CHAIN
    print('\n'+'='*50)
    print("STEP - 3: WRITER IS WORKING...")
    print("="*50, '\n')

    combined_report = (
        f"SEARCH RESULTS:\n {state['search_results']}",
        f"SCRAPED CONTENT:\n {state['scraped_content']}"
    )

    report = writer_chain.invoke({
        'topic':topic,
        'research': combined_report,
        'report': None,
        'feedback':None
    })

    state['report'] = report
    print(f"\nREPORT:\n{state['report']}")


    # CRITIC CHAIN
    print('\n'+'='*50)
    print("STEP - 4: FINDING THE ISSUES...")
    print("="*50, '\n')

    improvements = critic_chain.invoke({
        'report': state['report']
    })

    state['improvements'] = improvements
    print(f"\nCRITIC REPORT:\n{state['improvements']}")


    #FINAL REPORT
    print('\n'+'='*50)
    print("STEP - 5: WRITING FINAL REPORT...")
    print("="*50, '\n')
    
    final_report = writer_chain.invoke({
        'topic':None,
        'research': None,
        'report': state['report'],
        'feedback':state['improvements']
    })
    
    state['final_report'] = final_report
    print(f"\nFINAL REPORT:\n{state['final_report']}")

    return state


if __name__ == "__main__":
    topic = input("Enter a research topic: ")
    research_pipeline(topic)