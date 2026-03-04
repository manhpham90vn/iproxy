---
name: commit
description: Create commits following Conventional Commits standard for iProxy project
argument-hint: "[commit type or change description]"
---

## Commit Rules

Create commits following **Conventional Commits** format:

```
<type>(<scope>): <description>
```

### Type (required)

| Type       | Description                                      |
|------------|--------------------------------------------------|
| `feat`     | Add new feature                                 |
| `fix`      | Fix bug                                         |
| `docs`     | Documentation changes                           |
| `style`    | Code formatting, no logic changes               |
| `refactor` | Refactor code, no feature or bug fix           |
| `perf`     | Improve performance                             |
| `test`     | Add or fix tests                               |
| `build`    | Build system or dependencies changes            |
| `ci`       | CI/CD configuration changes                     |
| `chore`    | Other changes (no impact on src/test)           |

### Scope (optional)

Scope based on iProxy modules:
- **Backend**: `auth`, `accounts`, `proxy`, `models`, `db`, `api`, `security`, `config`, `redis`, `migration`, `routing`, `mcp`
- **Frontend**: `ui`, `dashboard`, `monitor`, `stats`, `keys`, `settings`
- **Infra**: `docker`, `ci`, `deps`

### Rules

1. Description in English, lowercase, no trailing period
2. Max 72 characters for first line
3. For breaking changes, add `!` after type/scope: `feat(api)!: change response format`
4. Body (optional) can be in English or Vietnamese

## Workflow

### Step 1: Check staged changes

- Run `git diff --staged --name-status` to see what's staged
- If already staged → proceed to step 2
- If NOT staged → ask user what to stage

### Step 2: Run lint/format based on staged file types

Check if staged files belong to `api/` or `admin/` (or both):

**If Python files (`api/`):**
- Run `cd api && ./format.sh` to check lint and format
- If lint errors → report to user and DO NOT commit until fixed
- Re-stage formatted files: `git add <staged .py files>`

**If TypeScript/JavaScript files (`admin/`):**
- Run `cd admin && ./format.sh` to check lint and format
- If errors → report to user and DO NOT commit until fixed
- Re-stage formatted files

**If both:**
- Run lint/format for both services

### Step 3: Analyze changes

- Classify staged files by type: code (.py, .ts, .tsx), docs (.md), config, migration, etc.
- If MANY different file types → merge into 1 commit with most general type
  - Priority: `feat` > `fix` > `refactor` > `chore` > `docs`
- If only 1 type → use appropriate type

### Step 4: Create commit message

- Determine type based on change content
- Determine scope based on affected directory/module
- If user provides `$ARGUMENTS`, use as hint for description
- Create message following Conventional Commits format

### Step 5: Commit

- Show commit message for user confirmation
- Run `git commit -m "<message>"`
