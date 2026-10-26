from langchain_core.messages import BaseMessage

IGNORED_BLOCK_TYPES = frozenset({"thinking", "reasoning"})


def flatten_content(message: BaseMessage) -> BaseMessage:
    """Turns a list of text blocks into a plain string, as the other providers return.

    Gemini answers with `[{"type": "text", "text": ...}]`; the services expect `message.content`
    to be a string. Messages with any other kind of block (images, tool calls as blocks) are
    returned unchanged, and tool calls, metadata and usage are never touched.
    """
    content = message.content
    if not isinstance(content, list):
        return message
    parts: list[str] = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(str(block.get("text", "")))
        elif isinstance(block, dict) and block.get("type") in IGNORED_BLOCK_TYPES:
            continue
        else:
            return message
    return message.model_copy(update={"content": "".join(parts)})
