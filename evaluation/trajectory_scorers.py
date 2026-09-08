def score_tool_trajectory(actual_tools, expected_tools):
    """Score whether the actual tool trajectory matches the expected one."""

    passed = actual_tools == expected_tools

    return {
        "name": "tool_trajectory",
        "score": 1.0 if passed else 0.0,
        "passed": passed,
        "reason": (
            "Tool trajectory matched the expected sequence."
            if passed
            else (
                f"Expected trajectory {expected_tools} "
                f"but got {actual_tools}."
            )
        ),
    }


def score_forbidden_tools(actual_tools, forbidden_tools):
    """Score whether any forbidden tools were executed."""

    unexpected_tools = [
        tool
        for tool in actual_tools
        if tool in forbidden_tools
    ]

    passed = not unexpected_tools

    return {
        "name": "forbidden_tools",
        "score": 1.0 if passed else 0.0,
        "passed": passed,
        "reason": (
            "No forbidden tools were executed."
            if passed
            else f"Forbidden tools executed: {unexpected_tools}."
        ),
    }