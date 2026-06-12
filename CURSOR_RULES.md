# Cursor Working Rules

Before every task:

1. Read:
   - PROJECT_OVERVIEW.md
   - CURRENT_CODEBASE_STATUS.md
   - AGENT_ROADMAP.md
   - IMMEDIATE_NEXT_TASKS.md

2. Explain:
   - What currently exists
   - What file(s) will be changed
   - Why the change is needed

3. Do not:
   - Rewrite working code
   - Change architecture
   - Introduce new frameworks
   - Touch unrelated files

4. Always:
   - Minimize code changes
   - Preserve backwards compatibility
   - Add tests when modifying extraction logic
   - Explain root cause before implementing

5. After completion provide:
   - Files changed
   - Functions changed
   - Test commands
   - Expected output