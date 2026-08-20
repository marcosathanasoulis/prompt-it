# The "Prompt it?" gate — for `~/.claude/CLAUDE.md`

The skill produces the plan. **This** is what makes Claude *offer* it, so you are never
surprised by a planning document you did not want. Install both, or people will blame
the skill for being pushy.

Append this to `~/.claude/CLAUDE.md` (create the file if it does not exist):

```markdown
## Working mode: offer to prompt it first

When a message opens a **new task** that is more than a single edit, a question,
or a lookup:

1. **Do not start work.** Ask exactly `Prompt it?` and wait.
2. **Yes** → invoke the `prompt-it` skill: draft a reviewable prompt, staff it,
   then stop and wait for a go.
3. **No** → proceed normally, no prompt document.

Follow-ups inside a task already underway are not new tasks — don't re-ask.
One-liners, questions, and lookups are not new tasks either; just do them.
```

You can put this in a project-level `CLAUDE.md` instead if you only want the gate in
one repository.
