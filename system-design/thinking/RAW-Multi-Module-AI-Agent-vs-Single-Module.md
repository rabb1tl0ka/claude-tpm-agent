---
date: 2026-02-14
type: thinking
author: Bruno
---

# Current Single Module POC State
The current POC state features a simple (by design) single module agent loop: SEND → READ → PROCESS → DRAFT → LOG.

The key disadvantages of this approach include:

1. huge context (and a tendency to grow as new AI agent features will be developed
2. huge number of tool use = huge token use = high costs for API AI model calls
3. trying to do a generic pass of **everything** that a TPM would do in **every** run is super inneficient -- there's no need to read slack, process msgs, draft msgs, send msgs in every run... as a matter of fact, I don't even see a thinking/reasoning step in the loop

 Again, I know that we designed this simple flow on purpose to keep things simple.
 I don't want to add complexity if a simpler solution is enough but the 1 test I did with the current version already showed me some really worrying signs:

 1. it did 21 runs OR 21 tool calls... it was not clear to me... but I think the log mentioned runs. I can't find any log files for the output of the AI agent... I don't think the AI agent was even generating any logs at that time...
 2. because of the 21 runs, I ran out of money in my Anthropic API account
 3. btw it did the 21 runs super fast so it made me wonder on the value of doing those 21 runs, one after the other, while(true), because the project state doesn't change that fast... so why keep repeating the same run/flow over and over?

Ok, now someone lookig at what I'm describing could suggest to just program a cron job that runs every 15 mins and it would solve the issue.
The problem is that I see more than just a lack of a cron job being setup...
I see the big problem of having the agent become this monolitic thing that follows a step-by-step script of things to do and there's little to no reasoning to it.

# The Road to a Better TPM AI Agent Solution

I started thinking about how I do my job as a TPM at Loka.
Quickly I realized that I don't follow a predictable step-by-step script of actions that I take every 15 mins.
What I do is based on a few different roles that I act as a TPM at Loka when I'm working with clients.

# The Multi Module Architecture

The multi module architecture understands that an AI Agent will have to leverage different modules to play different roles as a TPM.
This is required because in my job as a TPM, I also play different roles which require different ways of thinking to achieve the role's mission and goals.
The roles include:

- Delivery Manager Role: in charge of the delivery of the project that is aligned with the client's priorities and that enables the team to deliver the project on-time (<= planned finish date).
- Risk Manager Role: in charge of identifying risks that can impact the project and coming up with mitigation plans for them.
- Communication Manager role: in charge of creating Loka internal project status (traffic light updates), client status reports, using slack for updates from and to the client and team.
- Product Manager role: in charge of the scope of the project, the roadmap of features to be built, aligning priorities with the client and moving features from ideas, to requirements and to things that can be delivered (moving to the Delivery Manager to own)

## Common Things in ALL Roles

No matter the role, there's things in common in all of them:
- Mission: they all have a clear and unique mission to accomplish
- Goals: they have goals to achieve in pursuit of their mission
- Thinking Mode: they all need to think about how to achieve their goals in pursuit of their mission
- Comms Mode: they need to communicate with other roles, with the project team or client, and finally, with the Human TPM (we will call it Master User).
- Execution Mode: they need to take action(s) to achieve their goals
- Logging Mode: they need to log their activities in all modes (this is important for the Master User to have visibility about how they're performing their roles)
- Master User Preferences: configuration of how the Master User prefers that this role is done by the AI Agent

NOTE FOR CLAUDE: I'm not sure if these roles are played by a single agent OR if we should create an AI agent for every role and then have a master AI agent (like a mastermind) that orchestrates all AI agent roles. Please share the pros and cons of both options and what you would recommend and why.

## The Modes

### Thinking Mode
The AI agent must be able to think about the role that he's performing in any given moment.
The AI agent must be able to think about notes that the Master User drops in the role's inbox.

### Comms Mode
The AI agent must be able to communicate with other roles (or other AI Agents playing a role). For example, Delivery Manager role might need to tell the Risk Manager role that there's a massive delay in 1 task which might delay the project. The Risk Manager will then have to think about that risk. The Communication Manager will have to report that risk. 

### The Execution Mode
The AI agent will have to execute actions which might include the generation of notes specific for their work, invoking the execution of tools...

### The Logging Mode
The AI agent needs to log what they're doing for visibility and troubleshooting purposes.



