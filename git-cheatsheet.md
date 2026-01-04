# Git cheatsheet (template)

## Everyday basics

- Status: `git status`
- What changed: `git diff`
- Stage files: `git add .` (or `git add path/to/file`)
- Commit: `git commit -m "Message"`
- Pull latest (rebase): `git pull --rebase`
- Push: `git push`

## Branching

- List branches: `git branch -vv`
- Create + switch: `git switch -c feature/my-branch`
- Switch: `git switch main`
- Delete local branch: `git branch -d feature/my-branch`
- Delete remote branch: `git push origin --delete feature/my-branch`

## Logs and history

- Pretty log: `git log --oneline --decorate --graph --max-count=20`
- Show one commit: `git show <sha>`
- Blame: `git blame path/to/file`

## Tagging (release a template)

### Tag the current commit as `template1`

Annotated tag (recommended):

- Tag: `git tag -a template1 -m "template1"`
- Push just that tag: `git push origin template1`

If you want to tag a specific commit:

- `git tag -a template1 <sha> -m "template1"`
- `git push origin template1`

### List / inspect tags

- List tags: `git tag --list`
- Show tag details: `git show template1`

### Delete a tag

- Delete local tag: `git tag -d template1`
- Delete remote tag: `git push origin :refs/tags/template1`

### Checkout a tag (detached HEAD)

- `git checkout template1`

If you want a branch from the tag:

- `git switch -c from-template1 template1`

## Undo / fixups

- Unstage a file: `git restore --staged path/to/file`
- Discard local changes: `git restore path/to/file`
- Amend last commit message: `git commit --amend`

## Stash

- Stash: `git stash push -m "wip"`
- List stashes: `git stash list`
- Apply latest: `git stash pop`

## Remotes

- List remotes: `git remote -v`
- Add origin: `git remote add origin <url>`
