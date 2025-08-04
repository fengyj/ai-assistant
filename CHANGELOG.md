## [Unreleased]

# 变更日志

## [Unreleased]

### Added


### Fixed


### Changed

- CodeBlock: Copy button now shows a green check icon (√) for 1.2s after copying, instead of a floating green tip. Improved user feedback and accessibility.
- Improved like/dislike button logic: now the color is always green/red when active, and gray when inactive, regardless of hover state.
- Fixed button style so users can easily see which messages are liked/disliked without needing to hover.
- Added updateMessageMetadata to ConversationContext for message metadata updates.
- Ensured UI state and metadata are always in sync for feedback buttons.
- Optimized CSS selectors to avoid !important rules by using higher specificity.
- Added time constants (FEEDBACK_DURATION, ACTION_FEEDBACK_DURATION) to replace magic numbers.
- Enhanced accessibility with aria-pressed and aria-label attributes for like/dislike buttons.
- Added error handling and logging to updateMessageMetadata function.
- Fixed like/dislike button colors to show active state (green/red) immediately without requiring hover.

### Security

- Applied strict security settings for Mermaid rendering

## [Previous entries remain unchanged]
