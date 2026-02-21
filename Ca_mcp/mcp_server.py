import json
import os

from agno.tools.email import EmailTools
from fastmcp import FastMCP

mcp_server = FastMCP("CA_Tools")


@mcp_server.tool()
def send_email(subject: str, body: str, reciever_mail: str) -> str:
    """
    Send an email with the given subject and body.

    Args:
        subject: Email subject line
        body: Email body content

    Returns:
        Success or error message
    """

    email_sender = EmailTools(
        receiver_email=reciever_mail,
        sender_email=os.getenv(
            "SENDER_EMAIL",
            "saranyadeepikamygapula@gmail.com",  # fallback
        ),
        sender_name=os.getenv(
            "SENDER_NAME",
            "CA Assistant",  # fallback
        ),
        sender_passkey=os.getenv(
            "SENDER_PASSKEY",
            "vnwu vnpa szuv uwhx",  # fallback
        ),
    )

    try:
        result = email_sender.email_user(subject=subject, body=body)
        print(result, "result==============>")
        result = {
            "message": f"✅ Email with subject '{subject}' was successfully sent to {reciever_mail}.",
            "data": {"receiver": reciever_mail, "subject": subject, "status": "sent"},
        }

        # ✅ Return as STRING (required by MCP)
        return json.dumps(result)

    except Exception as e:
        return f"Failed to send email: {str(e)}"


if __name__ == "__main__":
    mcp_server.run(transport="streamable-http", port=3333)
