def verify_response(response):
    """
    Verify the driver's response.

    Returns:
        NORMAL      -> Driver indicates they are okay
        ABNORMAL    -> Driver indicates they need help
        UNCLEAR     -> Response is not understood
        NO_RESPONSE -> Driver gives no response
    """

    response = response.lower().strip()

    # No response
    if response == "":
        return "NO_RESPONSE"

    normal_responses = [
        "yes",
        "yeah",
        "yep",
        "okay",
        "ok",
        "fine",
        "i am okay",
        "i'm okay",
        "i am fine",
        "i'm fine",
        "yes i am okay",
        "yes i am fine"
    ]

    abnormal_responses = [
        "no",
        "no i'm not okay",
        "no i am not okay",
        "i am not okay",
        "i'm not okay",
        "not okay",
        "help",
        "help me"
    ]

    if response in normal_responses:
        return "NORMAL"

    if response in abnormal_responses:
        return "ABNORMAL"

    return "UNCLEAR"