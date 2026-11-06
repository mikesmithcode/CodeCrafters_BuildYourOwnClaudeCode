
import json
import subprocess

from app.skills import get_skill_body, apply_arg_substitution
from app.utils import debug_trace


"""-------------------------------------------------------------------------------------------------
functions to help with executing and responding to tool requests from LLM
----------------------------------------------------------------------------------------------"""
@debug_trace
def extract_tool_calls(message):
    """Extracts the tool_calls from the openai response"""
    try:
        if hasattr(message, "tool_calls") and message.tool_calls and len(message.tool_calls) > 0:
            return message.tool_calls
        return None
    except Exception as e:
        print(f"Error extracting tool_call: {e}")
        return None

@debug_trace
def handle_tool_calls(agent, tool_calls):
    """Executes tool calls requested by the LLM."""
    new_messages = []
    for tool_call in tool_calls:
        fn_name, tool_call_id, args = parse_tool_call(tool_call)
        
        if fn_name == 'Read':
            msg = Read(tool_call_id, args["file_path"])
        elif fn_name == 'Write':
            msg = Write(tool_call_id, args["file_path"], args["content"])  
        elif fn_name == 'Bash':
            msg = Bash(tool_call_id, args["command"])  
        elif fn_name == 'Skill':
            skill_name=args["name"]
            skill_args=args.get("args", "")
            
            msg = Skill(tool_call_id, skill_name, skill_args)
            skill_meta = agent.skills.get(skill_name, {})
            if skill_meta.get("context") == "fork":
                msg = agent.prompt_subagent(skill_name, msg)
        elif fn_name == 'LSP':
            msg=LSP(tool_call_id)
        else:     
            raise Exception(f"Tool not implemented: {fn_name}")
            
        new_messages.append(msg)
    return new_messages


def tool_response(tool_call_id, content):
    """Formats the output of tools to add to messages sent back to LLM"""
    return {"role": "tool",
            "tool_call_id": tool_call_id,
            "content": content}


def parse_tool_call(tool_call):
    """Extracts important info from a tool_call request"""
    fn_name = tool_call.function.name
    id = tool_call.id
    args = json.loads(tool_call.function.arguments)
    return (fn_name, id, args)



"""----------------------------------------------------------------------------------------------------
Tools
----------------------------------------------------------------------------------------------------"""

def Read(tool_call_id, filepath):
    with open(filepath, 'r') as f:
        return tool_response(tool_call_id, f.read())

def Write(tool_call_id, filepath, content):
    with open(filepath, 'w') as f:
        f.write(content)
        return tool_response(tool_call_id, "Ok")

def Bash(tool_call_id, command):
    #Options mean that stderr appears in stdout
    result = subprocess.run([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if not result.stdout.strip():
        msg = "Ok"
    else:
        msg = result.stdout
    return tool_response(tool_call_id, msg)

def Skill(tool_call_id, name, args=""):
    "Gets the skill body, substitutes the arguments and returns a msg"
    skill_body = get_skill_body(name)
    skill_body = apply_arg_substitution(skill_body, args)
    return tool_response(tool_call_id, skill_body)
    
def LSP(tool_call_id):
    content="LSP is not implemented yet"
    return tool_response(tool_call_id, content)
    

"""----------------------------------------------------------------------------------------------------
Advertise Tools
----------------------------------------------------------------------------------------------------"""

tool_list = [
                {
                    "type": "function",
                    "function": {
                        "name": "Read",
                        "description": "Read and return the contents of a file",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path to the file to read",
                                }
                            },
                            "required": ["file_path"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "Write",
                        "description": "Write content to a file",
                        "parameters": {
                        "type": "object",
                        "required": ["file_path", "content"],
                        "properties": {
                            "file_path": {
                            "type": "string",
                            "description": "The path of the file to write to"
                            },
                            "content": {
                            "type": "string",
                            "description": "The content to write to the file"
                            }
                        }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "Bash",
                        "description": "Execute a shell command",
                        "parameters": {
                        "type": "object",
                        "required": ["command"],
                        "properties": {
                            "command": {
                            "type": "string",
                            "description": "The command to execute"
                            }
                        }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                    "name": "Skill",
                    "description": "Load a skill's instructions into the conversation",
                    "parameters": {
                        "type": "object",
                        "required": ["name"],
                        "properties": {
                        "name": { "type": "string", "description": "The name of the skill to use" },
                        "args": { "type": "string", "description": "Optional arguments for the skill" }
                        }
                    }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "LSP",
                        "description": "Returns the file, line, and character where a symbol is defined.",
                        "parameters": {
                        "type": "object",
                        "properties": {
                            "operation": {
                            "type": "string",
                            "enum": ["goToDefinition"]
                            },
                            "filePath": {
                            "type": "string",
                            "description": "Absolute path, or a path relative to the agent's current working directory."
                            },
                            "line": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "1-based line number of the symbol."
                            },
                            "character": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "1-based character offset in UTF-16 code units (same as character count for ASCII)."
                            }
                        },
                        "required": ["operation", "filePath", "line", "character"]
                        }
                    }
                    }
            ]


