# Welcome to DocHub contributing guide

## Development workflow

Product management is done on GitHub issues.

Whenever you have an idea for a feature, please open an issue, this will enable others to
give their opinion on it too.

### Working on a feature

  * Make sure there an issue covering what you are going to write
  * Assign yourself to the issue so that others know you are working on it
  * Work inside feature branch
  * Maintain [CHANGELOG.md](CHANGELOG.md) up to date by adding at least a new line
  * Open a pull request to merge your branch into `main`.
    If it's not ready for prime time, don't worry, just mark it as a draft PR.
  * Link your PR with the issue

### Working on a bugfix

Whenever you code on a bugfix, the workflow is the same as a feature except:

 * Opening an issue is not mandatory
 * However, if an issue exists already, assign yourself to it

### Merging pull requests

If you have write permissions on the repository, you are free to merge immediately any *minor* pull requests that
seems of high enough quality and that passes the tests.

For *major* pull requests, we expect contributors to give their opinion via reviews before merging it.
While there is no absolute rule, it is better to wait for a week and/or 2 separate reviews before merging.
However, we acknowledge that it might sometime hard to collect enough feedback quickly enough.
In that case, use your judgment to see if you can override the previous rule.

What are *major/minor* pull requests ? Here again, we don't have any definite rule,
but as a rule of thumb, a bugfix is *minor* while making aesthetic changes, adding big features are *major*

## Deployment workflow

Update [CHANGELOG.md](CHANGELOG.md) to mint a new release from `main`,
then `git tag` with [CalVer](https://calver.org/) (format `YYYY.MM.MINOR`).

Then invoke C4 to deploy on the server in itself.
