# Disabled workflows

`ci.yml` here is the CI pipeline (backend lint+test, frontend lint+build). It
lives outside `.github/workflows/` because the git host token used to push did
not have the `workflow` OAuth scope.

To enable CI:

1. Grant the scope once: `gh auth refresh -h github.com -s workflow`
2. Move the file into place and push:
   ```bash
   git mv .github/workflows.disabled/ci.yml .github/workflows/ci.yml
   git commit -m "Enable CI workflow"
   git push
   ```
