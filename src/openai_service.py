from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.prompt import ChatPrompt

# Define a function to get the ChatOpenAI model
def get_chat_openai():
    return ChatOpenAI(model="gpt-4o", temperature=0)

def story_completion(story):
    model = get_chat_openai()
    prompt_template = PromptTemplate.from_template(ChatPrompt)
    chain = prompt_template | model |StrOutputParser()
    summary = chain.invoke({"story": story})
    return summary