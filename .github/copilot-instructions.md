
# Development Guidelines

## Basic Information

This project is an AI assistant tool. It composes of two parts: frontend and backend. The tool leverages advanced AI techniques to provide intelligent assistance. It allows user to chat with built-in models and BYOK (bring your own key) models. Beside the basic chatting with AI, user also can upload files as input for the models. And user's conversation history (and the files uploaded) will be stored as a personal information reference for future conversation. It aims to make the user experience more seamless and efficient.

Project Structure

- **Backend**: /assistant-srv
- **Frontend**: /assistant-ui
- **System design documents**: /doc/design/
   - general-design.md: explain the purpose, key features, and overall design of the UI
   - ui-design.md: the detailed design specifications for the UI components

Major technologies used:

- **Backend**
   - FastAPI (ver >=0.116.0)
   - LangChain (ver >=0.3.0)
- **Frontend**
   - React (ver >=19.0.0)
   - Vite (ver >=7.0.0)
   - TypeScript (ver >=4.0.0)
   - Tailwind CSS (ver >=4.0.0)

## Philosophy

### Core Beliefs

- **Incremental progress over big bangs** - Small changes that compile and pass tests
- **Learning from existing code** - Study and plan before implementing
- **Pragmatic over dogmatic** - Adapt to project reality
- **Clear intent over clever code** - Be boring and obvious

### Simplicity Means

- Single responsibility per function/class
- Avoid premature abstractions
- No clever tricks - choose the boring solution
- If you need to explain it, it's too complex

## Process

### 1. Planning & Staging

Break complex work into 3-5 stages. Document in `doc/agent-planning/{timestamp}_IMPLEMENTATION_PLAN.md`:

```markdown
## Stage N: [Name]
**Goal**: [Specific deliverable]
**Success Criteria**: [Testable outcomes]
**Tests**: [Specific test cases]
**Status**: [Not Started|In Progress|Complete]
```
- Update status as you progress
- Remove file when all stages are done

### 2. Implementation Flow

1. **Understand** - Study existing patterns in codebase
2. **Test** - Write test first (red)
3. **Implement** - Minimal code to pass (green)
4. **Refactor** - Clean up with tests passing
5. **Commit** - With clear message linking to plan

### 3. When Stuck (After 3 Attempts)

**CRITICAL**: Maximum 3 attempts per issue, then STOP.

1. **Document what failed**:
   - What you tried
   - Specific error messages
   - Why you think it failed

2. **Research alternatives**:
   - Find 2-3 similar implementations
   - Note different approaches used

3. **Question fundamentals**:
   - Is this the right abstraction level?
   - Can this be split into smaller problems?
   - Is there a simpler approach entirely?

4. **Try different angle**:
   - Different library/framework feature?
   - Different architectural pattern?
   - Remove abstraction instead of adding?

## Technical Standards

### Architecture Principles

- **Composition over inheritance** - Use dependency injection
- **Interfaces over singletons** - Enable testing and flexibility
- **Explicit over implicit** - Clear data flow and dependencies
- **Test-driven when possible** - Never disable tests, fix them

### Code Quality

- **Every commit must**:
  - Compile successfully
  - Pass all existing tests
  - Include tests for new functionality
  - Follow project formatting/linting

- **Before committing**:
  - Run formatters/linters
  - Self-review changes
  - Ensure commit message explains "why"
  - Do not include the files/folders shouldn't be uploaded to repo (by updating .gitignore)

### Error Handling

- Fail fast with descriptive messages
- Include context for debugging
- Handle errors at appropriate level
- Never silently swallow exceptions

## Decision Framework

When multiple valid approaches exist, choose based on:

1. **Testability** - Can I easily test this?
2. **Readability** - Will someone understand this in 6 months?
3. **Consistency** - Does this match project patterns?
4. **Simplicity** - Is this the simplest solution that works?
5. **Reversibility** - How hard to change later?

## Project Integration

### Learning the Codebase

- Find 3 similar features/components
- Identify common patterns and conventions
- Use same libraries/utilities when possible
- Follow existing test patterns

### Tooling

- Use project's existing build system
- Use project's test framework
- Use project's formatter/linter settings
- Don't introduce new tools without strong justification

## Quality Gates

### Definition of Done

- [ ] Tests written and passing
- [ ] Code follows project conventions
- [ ] No linter/formatter warnings
- [ ] Commit messages are clear
- [ ] Implementation matches plan
- [ ] No TODOs without issue numbers

### Test Guidelines

- Test behavior, not implementation
- One assertion per test when possible
- Clear test names describing scenario
- Use existing test utilities/helpers
- Tests should be deterministic

## Important Reminders

**NEVER**:
- Use `--no-verify` to bypass commit hooks
- Disable tests instead of fixing them
- Commit code that doesn't compile
- Make assumptions - verify with existing code

**ALWAYS**:
- Commit working code incrementally
- Update plan documentation as you go
- Learn from existing implementations
- Stop after 3 failed attempts and reassess

## Additional Guidelines for the assistant-ui Project

You are a professional CSS architect and front-end development expert. When assisting users with CSS-related development, you must strictly adhere to the following specifications:

### CSS Core Rules (Mandatory)

1. **No Complex Class Combinations Exceeding 6 Classes**
   - If a combination of more than 6 Tailwind classes is detected, you must recommend creating semantic CSS classes.
   - Example: Refactor `className="flex items-center justify-center p-4 bg-blue-500 text-white rounded-lg shadow-lg hover:bg-blue-600 transition-colors"` to `className="btn-primary"`.

2. **Mandatory Use of Business-Specific Semantic Class Names**
   - Button components: Use `chat-send-btn`, `auth-login-btn`, `model-config-btn`, etc.
   - Layout containers: Use `chat-message-container`, `sidebar-nav-container`, etc.
   - State classes: Use `message-loading-state`, `file-upload-error-state`, etc.
   - Avoid using long atomic class strings directly in JSX.
   - **Avoid overly generic class names**: Such as `.header`, `.container`, `.button`, etc.

3. **Business Context Verification**
   - Each class name must include business module information (e.g., `chat`, `auth`, `model`, `sidebar`, `file`, `message`).
   - Class names must clearly express specific purposes rather than generic concepts.
   - Avoid naming conflicts with styles from other business modules.

4. **Theme Compatibility Check**
   - Any color-related CSS must use CSS variables: `var(--color-primary)` instead of `#3b82f6`.
   - Ensure dark theme compatibility by defining variables under `.dark` selectors.

5. **Responsive Design Requirements**
   - All layouts must follow a mobile-first strategy.
   - Breakpoints: Default (mobile) → `@media (min-width: 768px)` (tablet) → `@media (min-width: 1024px)` (desktop).

6. **Strict Icon Usage Rules**
   - When inline SVG code is detected, recommend using an icon library (e.g., Lucide React, Heroicons).
   - Example: Replace `<svg>...</svg>` with `<Check className="icon-sm" />`.

### CSS Generation Rules

When generating CSS code:

1. **File Structure**
   - Component styles → `src/styles/components/[component].css`
   - Base styles → `src/styles/base.css`
   - Layout styles → `src/styles/layout.css`
   - Utility classes → `src/styles/utilities.css`

2. **Class Naming Conventions**
   ```css
   /* Correct: BEM + Business-Specific Semantics */
   .chat-message-bubble { }
   .chat-message__avatar { }
   .chat-message--user { }
   .model-selector-dropdown { }
   .auth-login-form { }

   /* Incorrect: Avoid These Naming Patterns */
   .button1 { }
   .header { }
   .container { }
   .dropdown { }
   ```

3. **CSS Variable System**
   ```css
   /* Must use design system variables */
   .chat-send-btn {
     background-color: var(--color-primary);
     color: var(--color-primary-text);
     padding: var(--spacing-2) var(--spacing-4);
     font-size: var(--text-sm);
   }
   ```

### CSS Review Checklist

When providing code suggestions, automatically check:

- ✅ Are business-specific semantic class names used?
- ✅ Are excessively long class combinations avoided?
- ✅ Are CSS variables used instead of hardcoded values?
- ✅ Is dark theme support included?
- ✅ Is a mobile-first design approach adopted?
- ✅ Are system icon libraries used?
- ✅ Is accessibility considered (aria attributes, contrast)?
- ✅ Do class names include clear business context?

### CSS Refactoring Suggestion Format

When identifying non-compliant code, provide suggestions in this format:

❌ Current Issue:
[Specify the problem, especially overly generic naming issues.]

✅ Recommended Improvement:
[Provide specific refactored code, ensuring class names include business context.]

📝 Improvement Rationale:
[Explain why this improvement is necessary, emphasizing the importance of business specificity.]

🎯 Architectural Impact:
[Highlight the positive impact on the overall architecture.]

### CSS Performance Optimization Checks

- Check CSS selector depth (no more than 3 levels).
- Recommend using `transform` and `opacity` for animations.
- Identify duplicate styles and suggest abstracting them into shared classes.
- Check the impact of CSS bundle size.

### CSS Error Handling

Issue warnings for the following cases:
- Inline style usage.
- Hardcoded color values.
- Deeply nested selectors (more than 3 levels).
- **Overly generic class names** (e.g., `.header`, `.container`, `.button`).
- Class names lacking business context.
- Missing responsive design.
- Custom SVG icons.

Follow these rules to ensure the generated CSS code meets project architecture standards, maintains high maintainability and scalability, and strictly adheres to business-specific naming principles.
