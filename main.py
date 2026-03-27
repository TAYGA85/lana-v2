from brain.personality import format_lana_reply
from brain.intent_router import detect_intent
from brain.response_builder import build_response
from memory.short_memory import ShortMemory
from core.state import LanaState
from core.session import SessionManager


def main():
    state = LanaState()
    memory = ShortMemory()
    session = SessionManager()

    print("LANA v2 booting...")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "exit":
            print("LANA: Goodbye.")
            break

        memory.add_user_message(user_input)

        intent = detect_intent(user_input, memory, session)
        raw_response = build_response(user_input, intent, memory, state, session)
        final_response = format_lana_reply(raw_response, state)

        memory.add_lana_message(final_response)
        print(f"LANA: {final_response}")


if __name__ == "__main__":
    main()