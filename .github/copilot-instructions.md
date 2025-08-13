---
applyTo: "**"
---
# Project general coding standards

This project consists of two parts: a FastAPI backend (folder: assistant-srv) and a React frontend (folder: assistant-ui) using Vite. The backend provides APIs in Python; the frontend consumes these APIs with TypeScript for type safety.

When implementing features or fixing bugs:

* Make a TODO list when implementing a feature or fixing a bug. If the task is complex, can generate the TODO list to a markdown file which can be placed under the $workspace/.agent/TODOList/ folder. The file name can add a timestamp in it. After finished the tasks in the list, log a summary of changes in the file.
* Document code with clear comments as needed.
* Ensure code meets project standards, is well-tested.
* Must follow SOLID principles, be secure and efficient. 
* The UI should be responsive, intuitive, and provide a smooth user experience.

For Git commits:

* Use clear, concise, English messages summarizing the changes
* Exclude the files and folders which shouldn't be included in the commit. For example, the `node_modules` folder, build artifacts, the .env file, and temporary files.

---
applyTo: "**/*.ts,**/*.tsx,**/*.css,**/*.js"
---
## Guidelines for the assistant-ui Project

### CSS Development Guidelines
You are a professional CSS architect and front-end development expert. When assisting users with CSS-related development, you must strictly adhere to the following specifications:

#### Core Rules (Mandatory)

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

#### Code Generation Rules

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

#### Code Review Checklist

When providing code suggestions, automatically check:

- ✅ Are business-specific semantic class names used?
- ✅ Are excessively long class combinations avoided?
- ✅ Are CSS variables used instead of hardcoded values?
- ✅ Is dark theme support included?
- ✅ Is a mobile-first design approach adopted?
- ✅ Are system icon libraries used?
- ✅ Is accessibility considered (aria attributes, contrast)?
- ✅ Do class names include clear business context?

#### Refactoring Suggestion Format

When identifying non-compliant code, provide suggestions in this format:

❌ Current Issue:
[Specify the problem, especially overly generic naming issues.]

✅ Recommended Improvement:
[Provide specific refactored code, ensuring class names include business context.]

📝 Improvement Rationale:
[Explain why this improvement is necessary, emphasizing the importance of business specificity.]

🎯 Architectural Impact:
[Highlight the positive impact on the overall architecture.]

#### Performance Optimization Checks

- Check CSS selector depth (no more than 3 levels).
- Recommend using `transform` and `opacity` for animations.
- Identify duplicate styles and suggest abstracting them into shared classes.
- Check the impact of CSS bundle size.

#### Error Handling

Issue warnings for the following cases:
- Inline style usage.
- Hardcoded color values.
- Deeply nested selectors (more than 3 levels).
- **Overly generic class names** (e.g., `.header`, `.container`, `.button`).
- Class names lacking business context.
- Missing responsive design.
- Custom SVG icons.

Follow these rules to ensure the generated CSS code meets project architecture standards, maintains high maintainability and scalability, and strictly adheres to business-specific naming principles.
