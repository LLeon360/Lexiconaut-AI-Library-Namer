from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Dict, Any
from dotenv import load_dotenv
import random

from models import LibraryName

load_dotenv()

async def generate_library_name(inputs: Dict[str, Any]) -> List[LibraryName]:
    model: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.7,
        max_tokens=100,
    )
    
    # Add a random element to the prompt
    random_seed = random.randint(1, 1000000)
    
    prompt: PromptTemplate = PromptTemplate.from_template(
        template="""
        I have a library that I need to create a clever and fitting name for. It is a {language} library that is used for {purpose}. The topic of the library is {topic}. Can you help me come up with {number_of_names} names for it? 
        
        By clever names, see if you can tie other word definitions to a library name. The name could even be a translation of a word that is relevant to the library's purpose. For example, if the library is used for a network scanner, you could call it Inquisitor. The library name does not necessarily have to include the language {language} or the topic {topic} and it should often be avoided if the library or purpose is outright inserted into the name. It's okay if it's some tie into the library such as Codebra (Code + Cobra and sounds like Cobra) for a Python library that works with code. Primarily focus on the purpose which is {purpose}.
        
        Try to avoid somewhat generic names that are simply what the library does. For example, if the library is used for a network scanner, avoid naming it NetworkScanner. Generic names like "SecureInsight" should also be avoided. Instead, try to come up with a name that is more creative and unique. 
        
        This is extremely important, do not return any names that already exist.
        
        Use this random seed for inspiration: {random_seed}
        
        Return an array of {number_of_names} JSON objects containing a name and explanation. (Do not surround the output with ```json ``` or any other code block.)
        """,
    )
    
    parser: JsonOutputParser = JsonOutputParser(pydantic_object=List[LibraryName])

    chain = prompt | model | parser
    result_dict: List[dict] = await chain.ainvoke({**inputs, "random_seed": random_seed})
    result: List[LibraryName] = [LibraryName(**item) for item in result_dict]
    
    return result