# Git Notes — Remotes and Collaboration

Diagram: [`git_collaboration.pdf`](git_collaboration.pdf)

A **remote** is a copy of the repository on a server (GitHub). Teammates share work through it.

```bash
git clone https://github.com/<user>/data-analysis-course.git   # first copy
git remote -v                                                   # list remotes
git fetch origin                                                # download, don't merge
git pull origin main                                            # fetch + merge
git push -u origin my-branch                                    # upload a branch
```

## The pull request workflow
1. Create a branch for your change: `git switch -c add-chart`.
2. Commit small, clear changes.
3. Push the branch and open a **pull request** (PR) on GitHub.
4. A teammate reviews and comments; you push fixes to the same branch.
5. When approved, the PR is merged into `main`.

## Habits for analysis projects
- Pull before you start working, push when you finish.
- Never commit passwords, API keys or private datasets — use `.gitignore`.
- Commit the *code* that produces results (and figures) rather than hand-edited outputs.
- Use `git blame file.py` to see who last changed each line, and `git log -p file.py` for its history.
