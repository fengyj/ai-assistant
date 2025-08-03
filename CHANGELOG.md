# 变更日志

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
- Replaced custom SVG copy icons with ClipboardDocumentIcon from @heroicons/react for consistency
- Removed shadows from code blocks by setting boxShadow: 'none' for cleaner appearance
- Simplified Mermaid chart rendering approach for better reliability
- Renamed SimpleMermaidChart to MermaidChart for better naming consistency
- UI jittering when typing with Mermaid diagrams in chat history  
- Page crashes caused by malformed Mermaid syntax
- Performance issues with repeated Mermaid rendering through global caching
- Mermaid diagrams not rendering correctly due to caching mechanism conflicts
- Image display issues - images now load properly after caching removal
- Complex error handling masking core rendering problems

### Changed

- Improved code block styling with header and copy button
- Enhanced Mermaid error handling - failed diagrams now display as code blocks instead of error messages
- Removed overly strict complexity limits for Mermaid diagrams (line count and node count restrictions)
- Extended Mermaid render timeout to 15 seconds for complex diagrams
- Increased Mermaid configuration limits (maxTextSize: 100000, maxEdges: 500)
- Enhanced theme support for all markdown elements including dark mode
- Added comprehensive error boundaries to prevent page crashes
- Simplified Mermaid implementation for better stability and reliability
- Improved Mermaid UI with loading indicators and better error states
- Removed global caching system that interfered with dynamic content rendering
- Updated user message color scheme to better match overall theme (gray instead of blue)
- Improved user message contrast: light gray background in light theme, dark gray in dark theme
- Updated Mermaid diagram color scheme to use neutral theme for better integration
- Improved code block styling: removed shadow effects for cleaner borders
- Enhanced code syntax highlighting with better contrast for light theme

### Security

- Applied strict security settings for Mermaid rendering
- Disabled HTML labels in flowcharts
- Limited text size and edge count to prevent DoS

## [Previous entries remain unchanged]
