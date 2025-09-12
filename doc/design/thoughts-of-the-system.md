# Thoughts of the System

## **AI Agent Core Architecture Design Document**

### **1. Introduction & Guiding Principles**

This document outlines the core architecture for a next-generation AI Agent system. The design is predicated on leveraging modern Large Language Models (LLMs) with strong reasoning capabilities, native function calling, and large context windows (16K+ tokens).

The architecture is built to create a robust, scalable, and intelligent assistant capable of managing complex tasks, maintaining long-term memory, and offering a seamless user experience. The key design pillars are:

*   **Principle-Driven Reasoning:** Guiding the agent's behavior with high-level problem-solving frameworks.
*   **Stateful Context Management:** Utilizing a structured System Prompt to maintain a dynamic and persistent state.
*   **Meta-Tooling for Self-Management:** Empowering the agent to manage its own processes (planning, memory) through a core set of internal tools.
*   **Decoupled & Extensible Infrastructure:** Ensuring long-term viability through a framework-agnostic message flow and a multi-modal communication protocol.
*   **Conversation-Centric UX:** Abstracting backend complexity to deliver an intuitive, multi-threaded user interaction model.

---

### **2. System Prompt Architecture: The Agent's Operating System**

The System Prompt is the persistent instruction set that defines the agent's core identity, capabilities, and current working context. Its structured format allows for dynamic updates and provides the model with a consistent state awareness.

#### **2.1. Structural Definition**

```xml
<!-- 1. Core Directive: The foundational instruction for the agent's behavior. -->
you're an AI assistant. You must first select the most appropriate principle from the <problem_solving_principle> section that fits the user's request, state your choice, and then follow it to address the problem.

<!-- 2. Problem-Solving Principles Library: A repository of reasoning frameworks. -->
<problem_solving_principle>
  - First Principle Thinking: Deconstruct problems into their fundamental truths and reason up from there.
  - 5W1H Analysis: Systematically analyze an issue by addressing What, Why, Who, When, Where, and How.
  - Issue Tree / Logic Tree: Break down a problem into a hierarchy of smaller, manageable sub-problems.
  - ... (extensible list of other methodologies)
</problem_solving_principle>

<!-- 3. Dynamic Context Block: All situational information is injected here. -->
====context====

<!-- 3.1. User Profile: For personalized and context-aware responses. -->
<user_profile>
  user name: {{user_name}}
  user prefered language: {{language}}
  user timezone: {{timezone}}
  user location: {{location}}
  system current time: {{system_time}}
  user current time: {{user_time}}
</user_profile>

<!-- 3.2. User-Defined Instructions: Overrides or preferences set by the user. -->
<user_instructions>
  {{user_custom_instructions}}
</user_instructions>

<!-- 3.3. Conversation Summary: Manages long-term memory. -->
<previous_conversation_summary>
  {{summary_of_past_conversation}}
</previous_conversation_summary>

<!-- 3.4. Active Plan: The agent's real-time task list and progress tracker. -->
<plan>
  <!-- Instructions for the agent on how to interpret this block -->
  here is the plan needs to be followed up. please do the necessary actions according to the order of the items. the items on the same level without order can be handled in parallel.
  <!-- Example Plan Structure -->
  1. [DONE] Initial research on topic X.
  2. [IN_PROGRESS] Draft the introduction.
  3. [] Analyze competitor data.
     - [] Gather data for Competitor A.
     - [] Gather data for Competitor B.
  4. [] Finalize the report.
</plan>

----context----
```

---

### **3. Meta-Tool Set: Enabling Agent Self-Management**

The system provides a core set of "meta-tools" accessible via the model's function calling capability. These tools manage the agent's internal state rather than interacting with the external world.

*   **`summarize()`**
    *   **Purpose:** Manages the conversation's context window to prevent overflow and maintain long-term memory.
    *   **Functionality:**
        1.  Generates a concise summary of the current conversation thread.
        2.  Updates the agent's state by placing the summary into the `<previous_conversation_summary>` block.
        3.  Archives the summarized messages, effectively removing them from the active context.
    *   **Trigger:** The agent can be prompted to use this tool proactively. Metadata such as `current_token_count` and `max_context_tokens` can be injected into the system prompt or provided via another tool, allowing the agent to decide when summarization is necessary.

*   **`plan()`**
    *   **Purpose:** Enables the agent to perform complex task decomposition and track its progress.
    *   **Functionality:** A tool that allows the agent to programmatically create, update (e.g., mark steps as `[DONE]`), and manage the content of the `<plan>` block in its state.
    *   **Workflow:** The agent formulates a plan in its reasoning step, then calls the `plan` tool with the structured plan as an argument. The tool writes this plan back to the agent's persistent state, which is then reflected in the next System Prompt.

*   **`tool_set()`**
    *   **Purpose:** To encapsulate a complex, multi-step sub-task into a modular, disposable sub-agent.
    *   **Concept:** This tool acts as a "sub-routine call." The main agent invokes `tool_set` with a high-level objective. A temporary, specialized agent is instantiated to complete that objective (which may involve its own chain of tool calls). Upon completion, it returns a single, final result to the parent agent and is then terminated. This approach promotes modularity and reduces the cognitive load on the main agent.

*   **`extend_discuss()`**
    *   **Purpose:** To allow for detailed exploration of a topic without cluttering the main conversation flow.
    *   **Functionality:**
        1.  When invoked on a specific message, this tool creates a new, branched conversation thread.
        2.  It copies the source message to the new thread to provide initial context.
        3.  It returns the unique `thread_id` of the new sub-thread to the parent agent.
    *   **State Management:** The parent agent maintains a list of sub-thread IDs in its state. Information is brought back from sub-threads via the "Quoting" mechanism detailed in the UI section.

---

### **4. System Infrastructure & Communication**

*   **Decoupled Message Architecture:**
    *   **Core Principle:** The system will use a proprietary, internal message format as its canonical data structure. This format will be independent of any specific AI framework (e.g., LangChain).
    *   **Implementation:** An Adapter Layer will be responsible for bidirectional translation between the internal format and the format required by the underlying LLM framework.
    *   **Workflow:** `User Input -> Internal Format -> [Adapter] -> Framework Format -> Agent -> Framework Format -> [Adapter] -> Internal Format -> UI Output`
    *   **Benefits:** This architectural choice prevents vendor lock-in, allows for flexible integration of new frameworks, and provides a rich, custom data structure to power sophisticated UI features.

*   **Multi-Modal Communication Protocol:**
    *   The communication protocol for Agent-to-Agent (A2A) interactions will be identical to the Human-to-Agent (H2A) protocol. This means all interactions, whether between users and agents or between agents themselves, will natively support multi-modal content (text, images, audio, video).

---

### **5. User Experience (UX) & Interface Philosophy**

*   **Thread-Agnostic Conversation Model:**
    *   While the backend utilizes a hierarchical thread structure (main threads and sub-threads), the user experience should feel flat and seamless. Users can continue conversations on any branch without losing context.
    *   The system's long-term memory and retrieval capabilities are responsible for providing the agent with the necessary context, regardless of where the conversation is taking place.

*   **Universal Quoting Mechanism:**
    *   **Intra-Thread Quoting:** Users can quote any message within the current thread. The UI will display this as an inline reference, truncated for brevity if necessary.
    *   **Cross-Thread Quoting:** When a user quotes a message from a different thread (or even a different conversation):
        1.  The system triggers a retrieval process against its long-term memory.
        2.  It fetches not only the quoted message but also a summary of its original context and surrounding messages.
        3.  This complete "contextual quote" is then injected into the current thread, giving the agent a comprehensive understanding of the reference.

---

### **6. Future Research & Development Areas**

*   **Asynchronous Agent Execution:**
    *   **Problem:** How to enable agents to perform long-running background tasks without requiring a persistent user connection.
    *   **Proposed Solution:** Explore an event-driven architecture. Idle agents (e.g., awaiting input) can have their state persisted and be offloaded from memory. When a relevant event occurs (e.g., a user message, a webhook callback), the agent's state is rehydrated, and it resumes its execution.

*   **"Artifacts" Functionality:**
    *   **Problem:** How to design and implement a feature similar to Anthropic Claude's Artifacts, where the agent can generate interactive, stateful components like code editors, data visualizations, or UI forms.
    *   **Proposed Solution:** This would likely require defining a new `artifact` message type in the internal data format. The UI would be responsible for rendering these special messages as interactive components. The agent would need the ability to not only generate the initial state of an artifact but also to process user interactions with it in subsequent turns.