from agents import (
    build_reader_agent,
    build_search_agent,
    build_writer_chain,
    build_critic_chain,
)


def _parse_agent_result(result):
    if isinstance(result, dict):
        for key in ("output", "result", "text", "content"):
            value = result.get(key)
            if value is not None:
                return str(value)
        if len(result) == 1:
            return str(next(iter(result.values())))
        return str(result)
    if isinstance(result, (list, tuple)):
        return "\n".join(str(item) for item in result)
    return str(result)


def run_research_pipeline(topic: str) -> dict:
    state = {}

    print("\n" + "=" * 50)
    print("step 1 - search agent is working ...")
    print("=" * 50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke(
        f"Find recent, reliable and detailed information about: {topic}"
    )
    state["search_results"] = _parse_agent_result(search_result)

    print("\n search result ", state["search_results"])

    print("\n" + "=" * 50)
    print("step 2 - Reader agent is scraping top resources ...")
    print("=" * 50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke(
        f"Based on the following search results about '{topic}', "
        f"pick the most relevant URL and scrape it for deeper content.\n\n"
        f"Search Results:\n{state['search_results'][:800]}"
    )
    state["scraped_content"] = _parse_agent_result(reader_result)

    print("\nscraped content: \n", state["scraped_content"])

    print("\n" + "=" * 50)
    print("step 3 - Writer is drafting the report ...")
    print("=" * 50)

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    state["report"] = _parse_agent_result(
        build_writer_chain().invoke(
            {
                "topic": topic,
                "research": research_combined,
            }
        )
    )

    print("\n Final Report\n", state["report"])

    print("\n" + "=" * 50)
    print("step 4 - critic is reviewing the report")
    print("=" * 50)

    state["feedback"] = _parse_agent_result(
        build_critic_chain().invoke({"report": state["report"]})
    )

    print("\n critic report \n", state["feedback"])
    return state


if __name__ == "__main__":
    topic = input("\n Enter a research topic: ")
    run_research_pipeline(topic)

