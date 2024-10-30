from dotenv import load_dotenv
load_dotenv()
from chains import generate_chain, reflect_chain
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from typing import Annotated, List, Sequence
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
from langgraph.graph import MessagesState


class State(TypedDict):
    messages: Annotated[list, add_messages]

def generate_node(state: State):
    return {'messages':[generate_chain.invoke(state)]}


def reflect_node(state: State):
    map_messages={'ai':HumanMessage, 'human':AIMessage}
    messages=[state['messages'][0]]+[map_messages[msg.type](msg.content)  for msg in state['messages'][1:]]
    reflection= reflect_chain.invoke({"messages": messages})
    return {'messages':[HumanMessage(content=reflection.content)]}

def should_continue(state: State):
    if len(state['messages']) <= 6:
        return 'reflect'
    return END

builder = StateGraph(State)
builder.add_node('generate', generate_node)
builder.add_node('reflect', reflect_node)
builder.add_edge(START, 'generate')

builder.add_conditional_edges('generate', should_continue)
builder.add_edge('reflect', 'generate')


memory= MemorySaver()
builder.compile(checkpointer=memory)


graph = builder.compile()

request = HumanMessage(content="write about langchain")

for event in graph.stream({"messages": [request]},{'configurable':{'thread_id': '123'}}):
    print(event)