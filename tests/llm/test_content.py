from langchain_core.messages import AIMessage

from ai_lib.llm.content import flatten_content


def test_text_blocks_become_a_string():
    message = AIMessage(content=[{"type": "text", "text": "ol"}, {"type": "text", "text": "á"}])

    assert flatten_content(message).content == "olá"


def test_extras_and_thinking_blocks_are_dropped():
    message = AIMessage(
        content=[
            {"type": "thinking", "thinking": "pensando"},
            {"type": "text", "text": "ok", "extras": {"signature": "abc"}},
        ]
    )

    assert flatten_content(message).content == "ok"


def test_plain_strings_inside_the_list_are_kept():
    assert flatten_content(AIMessage(content=["a", {"type": "text", "text": "b"}])).content == "ab"


def test_string_content_is_returned_as_is():
    message = AIMessage(content="texto")

    assert flatten_content(message) is message


def test_unknown_blocks_leave_the_message_unchanged():
    message = AIMessage(content=[{"type": "text", "text": "x"}, {"type": "image", "url": "u"}])

    assert flatten_content(message) is message


def test_tool_calls_and_metadata_survive():
    message = AIMessage(
        content=[{"type": "text", "text": "usando ferramenta"}],
        tool_calls=[{"name": "buscar", "args": {"q": "sol"}, "id": "1", "type": "tool_call"}],
        response_metadata={"model_name": "m"},
    )

    result = flatten_content(message)

    assert result.content == "usando ferramenta"
    assert result.tool_calls == message.tool_calls
    assert result.response_metadata == {"model_name": "m"}
