## Summary: Tools vs. Skills in Your Agent Architecture

FeatureTools (Read, Write, Bash, Skill)

## 1. What is a Tool?
Tools are the hard primitives of your agent. They are explicitly defined with strict argument structures (parameters, types, and descriptions) that the LLM understands natively.Examples: Read (reads a file path), Write (writes content), Bash (runs shell commands), and the meta-tool Skill.Execution flow: The LLM outputs a structured tool call request -> your Python backend parses it -> your code runs the underlying function and returns a result message with role tool.

## 2. What is a Skill?
Skills are soft, modular instructions stored in markdown files (SKILL.md) with frontmatter metadata (name, description, and optional context: fork).Discovery: During startup, your crawl_skills() function parses only the frontmatter to build a lightweight catalog, keeping startup fast.Invocation: The LLM reads the skill catalog in the system prompt. When it wants to use a skill, it calls the generic Skill tool passing the skill's name.The Body & Scripts: A skill contains a markdown body of instructions. When retrieved:It can perform argument substitution (like $ARGUMENTS, $0, $1).If the skill has context: fork, it launches an isolated subagent loop (using a fresh instance of your Agent class) with the skill's body serving as its initial prompt.Within that subagent or main loop, the instructions can direct the agent to execute code, run commands via Bash, or parse outputs, effectively letting a skill orchestrate multi-step programmatic workflows.

## 3. How They Work Together
The System Prompt gives the LLM the catalog of Skills.The LLM matches a user request to a skill and calls the Skill tool.Your Tool Handler looks up the skill, reads its body/script on demand, and either injects it or hands it off to an isolated Subagent (context: fork).During its execution, that skill's workflow can freely invoke Tools (like Bash or Read) to get its job done before returning a final answer back to the main conversation.