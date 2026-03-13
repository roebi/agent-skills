---
name: create-questions-and-answers-en
version: 1.0.0
description: >
  Runs a structured Q&A loop with a user: prompts them for questions one at a
  time, answers each question, then compiles all questions and answers into a
  downloadable Markdown file at the end. Use this skill whenever a user wants
  to test a configuration, probe knowledge, document a session, or explore a
  topic interactively. Activate for phrases like: "let us do a Q&A", "ask me
  questions", "I have questions for you to answer", "test my setup with
  questions", "compile a Q&A document", or "end of questions".
license: CC BY-NC-SA 4.0
language: en
author: roebi (Robert Halter)
attribution: >
  Part of the roebi agent-skills library.
  https://github.com/roebi/agent-skills
spec: https://agentskills.io/specification
compatibility: Requires file output capability (bash or file_create tool).
metadata:
  author: roebi
  spec: https://agentskills.io/specification
---

# Create Questions and Answers

Guides an agent through a structured, iterative Q&A session with a user and
produces a downloadable Markdown file containing all questions and answers.

## When to use this skill

Activate when the user:
- Wants to test a system prompt, configuration, or knowledge base
- Wants to document a topic through guided questions
- Asks for a Q&A loop, question-answer session, or interview-style interaction
- Mentions "end of questions" as a termination signal
- Wants a compiled, downloadable record of the conversation

## Step-by-step instructions

### 1. Confirm understanding

At the start, briefly confirm the loop to the user:
- You will prompt them to supply questions one at a time
- You will answer each question
- The loop repeats until the user says **"end of questions"**
- You will then compile everything into a downloadable `.md` file

### 2. Run the Q&A loop

Repeat this cycle until termination:

```
1. Prompt the user: "Ready — go ahead with your next question."
2. User writes the question.
3. Agent answers the question thoroughly and accurately.
4. Return to step 1.
```

**Rules during the loop:**
- Answer each question before asking for the next one — never batch questions
- Use web search or tools if the question requires current or external information
- Cite sources where relevant
- Keep answers focused; avoid padding

### 3. Detect termination

The loop ends when the user writes any of:
- `end of questions`
- `no more questions`
- `that's all`
- `done`

### 4. Compile the Markdown file

Once the loop ends, create a `.md` file containing:

```markdown
# Q&A Session: <topic or session title>

> <optional: brief description of the session context>
> Date: <YYYY-MM-DD>

---

## Q1: <Short question title>

**Question:**
<Full question text>

**Answer:**
<Full answer text>

---

## Q2: <Short question title>
...
```

**File naming convention:**
```
<topic-slug>-qa-session.md
# Examples:
#   systemprompt-qa-session.md
#   agent-skills-qa-session.md
#   project-review-qa-session.md
```

### 5. Deliver the file

- Save the file to the output directory
- Present it to the user using the `present_files` tool
- Provide a one-sentence summary of how many questions were covered

## Output format rules

- Use `## Q<N>: <title>` headings for each entry
- Bold `**Question:**` and `**Answer:**` labels
- Separate entries with `---`
- Preserve the full original question text verbatim
- Preserve the full answer including any tables, lists, or code blocks
- Include a session header with topic and date

## Examples

### Good session opener

> "Understood! Here's the loop: you give me a question, I answer it, we repeat
> until you say 'end of questions', then I compile everything into a `.md` file.
> Ready — go ahead with your first question!"

### Good termination handling

User: `end of questions`

Agent: *(immediately stops the loop, compiles the file, presents it)*
"All N questions compiled into `<topic>-qa-session.md`."

### Anti-patterns to avoid

- ❌ Asking multiple questions at once
- ❌ Answering before the user has submitted their question
- ❌ Skipping the compiled file output
- ❌ Truncating long answers in the output file
- ❌ Forgetting the session date in the header

## Reference files in this skill

- `references/output-format.md` — extended Markdown output formatting guide
