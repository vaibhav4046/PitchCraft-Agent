# Contributing — conflict-free workflow (Arman, read this)

The merge conflicts happened for ONE reason: **two diverging forks.** Arman worked on his own fork's
`ticketguard` while 50+ commits landed on the canonical `ticketguard` at the same time, so the branches
drifted apart and a cross-fork PR conflicted. The fix is simple: **one repo, one branch, always start from latest.**

## The golden rules
1. **Use the canonical repo only:** `https://github.com/vaibhav4046/PitchCraft-Agent` — **do NOT fork it.**
   (Vaibhav: add Arman as a collaborator — Settings → Collaborators → Add `SyedArmanAli2003` → Write.)
2. **The live branch is `ticketguard`.** That's what's deployed. Work there.
3. **Always pull before you work, always pull before you push.**

## Clone once
```bash
git clone https://github.com/vaibhav4046/PitchCraft-Agent.git
cd PitchCraft-Agent
git checkout ticketguard
```

## Every work session
```bash
git checkout ticketguard
git pull origin ticketguard          # get everyone's latest FIRST — this prevents conflicts
# ... make your changes ...
git add -A && git commit -m "feat: <what you did>"
git pull --rebase origin ticketguard # re-sync in case someone pushed while you worked
git push origin ticketguard          # direct push (you have write access now)
```
Because you have write access, **commit straight to `ticketguard` — no fork, no cross-repo PR, no conflict.**

## If you prefer a PR (optional, for review)
```bash
git checkout ticketguard && git pull origin ticketguard   # branch FROM latest
git checkout -b feat/my-thing
# ... commit ...
git push origin feat/my-thing
gh pr create --base ticketguard --fill
gh pr merge --auto --squash        # auto-merges the moment checks pass + no conflict
```
The repo now has **auto-merge**, the **"Update branch"** button, and **auto-delete of merged branches** enabled,
so a PR branched from latest merges itself cleanly. If GitHub ever shows the PR is behind, click **Update branch**
(or `gh pr update-branch`) before merging.

## What NOT to do (this is what caused the pain)
- ❌ Don't fork and let your fork sit for days while the main branch moves — it WILL diverge and conflict.
- ❌ Don't open a cross-fork PR from a stale branch.
- ❌ Don't resolve conflicts by "Accept current/incoming" blindly — that silently drops the other person's work
  (that's how the share-report feature got lost). If you must resolve, keep BOTH sides.

## Current state (2026-06-07)
- All PRs resolved (1,2,4,5 merged · 3,6 closed). `main` == `ticketguard`. No open PRs, no conflicts.
- Your two priority tasks are in `ARMAN_HANDOFF.md`: (1) fresh Gemini key in Render, (2) Atlas search indexes.
- PR #6's "shareable report + image analysis" was closed and your fork is gone — if you still want that feature,
  re-apply it on top of the current `ticketguard` (branched from latest) and it won't conflict.
