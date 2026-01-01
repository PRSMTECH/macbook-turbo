# Decision Log

## 2026-01-01 - README Styling Approach

**Context**: Need to make README accessible for first-time macOS users who may not know how to use Terminal
**Decision**: Add explicit step-by-step walkthrough with expandable sections
**Rationale**:
- Many macOS users never open Terminal
- "How to open Terminal" removes friction for absolute beginners
- Expandable `<details>` keeps advanced info accessible but not overwhelming
- Color explanation table gives immediate understanding
**Alternatives**:
- Video tutorial (higher maintenance, not inline)
- Shorter README (would lose beginners)
**Impact**: Lower barrier to entry for non-technical users

## 2026-01-01 - PRSMTECH Visual Styling

**Context**: README needed brand consistency with other PRSMTECH projects
**Decision**: Apply standard PRSMTECH styling (typing SVG, capsule-render, cyan theme)
**Rationale**:
- Consistent brand identity across projects
- Animated header is eye-catching
- Cyan (#00D4FF) is distinctive and readable
**Alternatives**:
- Keep minimal styling (less memorable)
- Use different color scheme (inconsistent)
**Impact**: Better brand recognition, more professional appearance

## 2026-01-01 - Dynamic Path Resolution

**Context**: App had hardcoded `/Users/bigswizz/` paths that would break for other users
**Decision**: Use `os.path.dirname(os.path.abspath(__file__))` for dynamic path resolution
**Rationale**:
- Works regardless of install location
- Standard Python pattern for this use case
- No user configuration required
**Alternatives**:
- Environment variables (extra setup)
- Config file (extra complexity)
**Impact**: App now works for all users without modification (CRITICAL FIX)

## 2026-01-01 - One-Line Installer Pattern

**Context**: Needed easy installation for users unfamiliar with git/pip
**Decision**: Create curl-based one-line installer
**Rationale**:
- Industry standard (Homebrew, oh-my-zsh use same pattern)
- Single command to copy/paste
- Handles all setup automatically
**Alternatives**:
- Homebrew formula (requires separate tap)
- Manual instructions only (higher friction)
**Impact**: Dramatically reduced installation friction

## 2025-12-27 - GitHub Repository Naming

**Context**: Deploying cpu-monitor to fresh GitHub repository
**Decision**: Named repository "macbook-turbo" in PRSMTECH organization
**Rationale**:
- More marketable/memorable name than "cpu-monitor"
- Reflects the turbo/optimization focus
- Matches the product positioning as a performance toolkit
**Alternatives**:
- cpu-monitor (too generic)
- mac-optimizer (less catchy)
- performance-toolkit (too long)
**Impact**: Better branding for potential open-source adoption

## 2025-12-27 - License Selection

**Context**: Needed to choose license for open-source release
**Decision**: MIT License
**Rationale**:
- Maximum permissiveness for adoption
- Standard for utility tools
- No restrictions on commercial use
**Alternatives**:
- Apache 2.0 (more complex)
- GPL (too restrictive)
**Impact**: Easy for anyone to use/modify/distribute

## 2025-12-27 - Repository Structure

**Context**: Organizing files for public consumption
**Decision**: Keep flat structure with modules/ subdirectory
**Rationale**:
- Simple for new users to understand
- .command files at root for discoverability
- modules/ contains advanced components
**Impact**: Easy onboarding for users
