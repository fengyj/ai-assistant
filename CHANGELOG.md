# 变更日志

## [Unreleased]

### Added

## [Unreleased]

### Added
- Basic markdown rendering with syntax highlighting support
- Table support via remark-gfm plugin  
- Mermaid diagram rendering with error handling and timeouts
- Copy functionality for code blocks and diagrams
- Performance optimization with React.memo to prevent UI jittering
- Complete UI color scheme coordination with gray theme
- Enhanced code block styling improvements with clean borders and improved contrast
- Icon-based copy buttons for code blocks and Mermaid diagrams with hover-to-show functionality

### Fixed
- Updated syntax highlighting theme from 'tomorrow' to 'vs' for better readability
- Replaced text-based copy buttons with ClipboardDocumentIcon from Heroicons
- Implemented hover-to-show functionality for copy buttons
- Removed all shadow effects from code blocks (box-shadow: none)
- Simplified Mermaid rendering to use direct rendering instead of iframe for better stability
- Ensured all copy buttons use consistent styling with rest of the interface

### Fixed

- UI jittering when typing with Mermaid diagrams in chat history  
- Page crashes caused by malformed Mermaid syntax
- Performance issues with repeated Mermaid rendering through global caching
- **[NEW]** Mermaid diagrams not rendering correctly due to caching mechanism conflicts
- **[NEW]** Image display issues - images now load properly after caching removal
- **[NEW]** Complex error handling masking core rendering problems

### Changed

- Improved code block styling with header and copy button
- Enhanced Mermaid error handling - failed diagrams now display as code blocks instead of error messages
- Removed overly strict complexity limits for Mermaid diagrams (line count and node count restrictions)
- Extended Mermaid render timeout to 15 seconds for complex diagrams
- Increased Mermaid configuration limits (maxTextSize: 100000, maxEdges: 500)
- Enhanced theme support for all markdown elements including dark mode
- Added comprehensive error boundaries to prevent page crashes
- **[NEW]** Simplified Mermaid implementation for better stability and reliability
- **[NEW]** Improved Mermaid UI with loading indicators and better error states
- **[NEW]** Removed global caching system that interfered with dynamic content rendering
- **[NEW]** Updated user message color scheme to better match overall theme (gray instead of blue)
- **[NEW]** Improved user message contrast: light gray background in light theme, dark gray in dark theme
- **[NEW]** Updated Mermaid diagram color scheme to use neutral theme for better integration
- **[NEW]** Improved code block styling: removed shadow effects for cleaner borders
- **[NEW]** Enhanced code syntax highlighting with better contrast for light theme

### Security

- Applied strict security settings for Mermaid rendering
- Disabled HTML labels in flowcharts
- Limited text size and edge count to prevent DoS

## [Previous entries remain unchanged]
