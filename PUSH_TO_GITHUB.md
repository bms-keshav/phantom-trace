# Push PHANTOM TRACE to GitHub

Run from project root:

```powershell
git add .
git commit -m "Initial PHANTOM TRACE hackathon build"
```

After you create/share your GitHub repository URL:

```powershell
git remote add origin <YOUR_REPO_URL>
git branch -M main
git push -u origin main
```

If remote already exists:

```powershell
git remote set-url origin <YOUR_REPO_URL>
git push -u origin main
```
