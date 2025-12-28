# Product Context

**Project**: MacBook Turbo
**Repository**: https://github.com/PRSMTECH/macbook-turbo
**Last Updated**: 2025-12-27

## Overview

MacBook Turbo is a comprehensive macOS system optimization toolkit that provides real-time CPU, memory, and thermal monitoring through an elegant menu bar app, combined with intelligent process management that protects developer workflows.

## Problem Statement

macOS can slow down due to:
- Runaway processes consuming CPU
- Memory pressure from accumulated apps
- Bloated caches from browsers/dev tools
- Background processes developers forget about

Traditional cleanup tools often kill important development processes, causing lost work.

## Solution

A developer-friendly optimization toolkit that:
1. Monitors system health in real-time via menu bar
2. Protects IDEs, terminals, and dev tools from cleanup
3. Uses multi-factor scoring to identify cleanup candidates
4. Provides both automatic and manual cleanup modes

## Tech Stack

- **Python 3.9+**: Core language
- **rumps**: macOS menu bar integration
- **psutil**: Cross-platform system monitoring
- **Shell scripts**: Quick operations and CLI tools
- **LaunchAgent**: Auto-start capability

## Architecture

```
┌─────────────────────────────────────────┐
│           Menu Bar App (rumps)          │
├─────────────────────────────────────────┤
│  Thermal  │  Memory  │  Disk  │ Process │
│  Monitor  │  Monitor │ Cleaner│  Scorer │
├─────────────────────────────────────────┤
│              psutil / macOS APIs        │
└─────────────────────────────────────────┘
```

## Key Features

1. **Real-time Monitoring**: CPU/Memory/Thermal in menu bar
2. **Developer Protection**: Whitelists 30+ dev tools
3. **Smart Cleanup**: Multi-factor scoring algorithm
4. **Auto-Cleanup Modes**: 4 configurable thresholds
5. **Disk Cleanup**: 30+ cache locations
6. **Modular Design**: Use only what you need

## Target Users

- Software developers using macOS
- Power users with multi-monitor setups
- Claude Code users needing performance optimization
- Anyone experiencing macOS slowdowns

## Differentiation

| Feature | MacBook Turbo | CleanMyMac | Others |
|---------|--------------|------------|--------|
| Developer Protection | ✅ Built-in | ❌ | ❌ |
| Free & Open Source | ✅ | ❌ | Varies |
| Menu Bar Integration | ✅ | Limited | Varies |
| Auto-Cleanup Modes | ✅ 4 levels | ❌ | ❌ |
| Modular Architecture | ✅ | ❌ | ❌ |
