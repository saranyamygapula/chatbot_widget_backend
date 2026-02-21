from models.Model import AgentContext, Message

from .decision_table import DECISION_TABLE


def build_message(content: str, additional_kwargs=None):
    return Message(
        content=content,
        additional_kwargs=additional_kwargs or {},
    )


async def handle_purchase_resume(
    *,
    state: AgentContext,
    tool_name: str,
    user_response: str,
) -> dict:
    tool_rules = DECISION_TABLE.get(tool_name)
    if not tool_rules:
        return {"type": "CONTINUE"}

    key = user_response.strip().upper()
    rule = tool_rules.get(key) or tool_rules.get("__DEFAULT__")

    message = build_message(
        rule["content"].format(user_response=user_response),
        additional_kwargs={
            "tool": tool_name,
            "decision": rule["decision"],
        },
    )

    # try:
    #     message = await analyse_sentiment(
    #         sent_input_message=build_message(user_response),
    #         output_message=message,
    #         details=state,
    #     )
    # except Exception:
    #     pass

    return {
        "type": "END",
        "message": message,
    }
