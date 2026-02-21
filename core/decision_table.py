DECISION_TABLE = {
    "purchase_subscription": {
        "LIMIT_REACHED": {
            "content": (
                "You have reached the maximum limit of 2 subscriptions. "
                "Please wait for your current subscriptions to expire or contact support."
            ),
            "decision": "LIMIT_REACHED",
        },
        "MANUAL": {
            "content": "Please provide your card number to proceed with the payment.",
            "decision": "MANUAL",
        },
        "YES": {
            "content": "Please provide your card number to proceed with the payment.",
            "decision": "YES",
        },
        "NO": {
            "content": "I have cancelled your purchase. Feel free to purchase anytime.",
            "decision": "NO",
        },
    },
    "cancelOrder": {
        "NOT_EXIST": {
            "content": (
                "We couldn’t find an order with the ID you entered. "
                "Please verify the order ID and try again."
            ),
            "decision": "NOT_EXIST",
        },
        "ALREADY_CANCELLED": {
            "content": "This order has already been cancelled.",
            "decision": "ALREADY_CANCELLED",
        },
        "NO": {
            "content": (
                "The cancellation has been reversed. You can cancel later if required."
            ),
            "decision": "NO",
        },
        "__DEFAULT__": {
            "content": (
                "✅ Order has been successfully cancelled.\n\n"
                "Reason: **{user_response}**"
            ),
            "decision": "CONFIRMED",
        },
    },
}
