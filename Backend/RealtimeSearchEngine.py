from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

Username = os.getenv("Username")
Assistantname = os.getenv("Assistantname")
Groq_API_Key = os.getenv("GROQ_API_KEY")  # Changed from Groq_API_Key


# Check if API key exists
if not Groq_API_Key:
    print("Error: GROQ_API_KEY not found in .env file")
    print("Please check that your .env file contains: GROQ_API_KEY=your_api_key")
    exit(1)

client = Groq(api_key=Groq_API_Key)

# Create Data directory if it doesn't exist
os.makedirs("Data", exist_ok=True)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)
    messages = []

def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are :\n[start]\n"

    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

    Answer += "[end]"
    return Answer

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, Sir, how can I help you?"}
]

def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data += f"Use This Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours: {minute} minutes: {second} seconds.\n"
    return data

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
    messages.append({"role": "user", "content": f"{prompt}"})

    search_context = GoogleSearch(prompt)  # may be empty

    messages_for_llm = [
        {"role": "system", "content": "You are Jarvis. Use the web search context if provided."},
        {"role": "system", "content": f"Web search context:\n{search_context}"},
        {"role": "user", "content": prompt},
    ]

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages_for_llm,
    )

    Answer = completion.choices[0].message.content.strip()
    return Answer


    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    SystemChatBot.pop()
    return AnswerModifier(Answer=Answer)

if __name__ == "__main__":
    while True:
        prompt = input("Enter Your Query: ")
        print(RealtimeSearchEngine(prompt))