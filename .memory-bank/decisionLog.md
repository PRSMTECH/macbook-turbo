# Decision Log

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
