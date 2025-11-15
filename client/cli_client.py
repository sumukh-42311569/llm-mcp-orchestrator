import httpx

BASE_URL = "http://127.0.0.1:8000"

def main():
    print("=== MCP Client ===")
    while True:
        task_type = input("Enter task (summarize/explain_code/generate_code or 'q' to quit): ")
        if task_type.lower() == "q":
            break

        content = input("Enter text/code:\n")
        payload = {"task_type": task_type, "content": content}

        response = httpx.post(f"{BASE_URL}/process/", json=payload)
        print("\n--- Result ---")
        print(response.json().get("result"))
        print()

if __name__ == "__main__":
    main()
