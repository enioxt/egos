# Git Layer Architecture — Reference

> **Origin:** EGOS Self (Mar 2026) | **Status:** PAUSED — egos-self repo under security review, no active development
> **Full spec:** `/home/enio/egos-self/docs/GIT_LAYER_ARCHITECTURE.md`

## Evolution Path

```
Phase 1 (NOW)       Phase 2 (NEXT)        Phase 3 (FUTURE)
GitHub API    →     GitHub OR Forgejo  →  Any Git host / P2P
```

## Core Abstraction

```python
class GitProvider(ABC):
    def authenticate(self) -> bool: ...
    def list_repos(self) -> list[Repo]: ...
    def create_repo(self, name: str) -> Repo: ...
    def push_file(self, repo, path, content) -> bool: ...

class GitHubProvider(GitProvider): ...   # Phase 1
class ForgejoProvider(GitProvider): ...  # Phase 2
class LocalGitProvider(GitProvider): ... # Phase 3
```

## Principle

Start with GitHub (everyone has an account).
Graduate to self-hosted (when you want independence).
Federate with others (no central authority).

## Security Model

- Tokens stored locally (~/.config/egos-self/) with 600 permissions
- Token never leaves device, never sent to any EGOS server
- TLS for GitHub API, WSS for relay, SSH for git
