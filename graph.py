from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv("OPENAI_API_KEY"))
if __name__ == '__main__':
    print("Hello, World!") 
    # testing