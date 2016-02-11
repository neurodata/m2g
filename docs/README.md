# How to Build Docs

The `ndmg` directory should have a sister directory `ndmg-docs` at the same level, which is checked out to the `gh-pages` branch.

```
# from ndmg directory:
sphinx-apidoc -o ./docs/source ./ndmg/
cd docs
make html
```
