# Contributing to M2G

This document is a working draft.  Edits and comments welcome. See the [neurodata practices](https://github.com/neurodata/practices) for best practices on writing code.

## Driving Principles
bids, pythonic

1. Any code from NeuroData (eg, written based on work here, and therefore funded by our funders, rather than for fun), live in a neurodata controlled org, rather than a personal repo (much like if you worked at google or a startup).
2. Everything is always a PR, never a direct commit to master
3. People using the code should always use deploy, if you have some branch that you think is better than deploy for some reason, then it is your responsibility to make a PR to deploy, rather than encouraging other people to use some untested branch. that is, unless you want them to be testing for you, which is a different thing.

## Branches
### deploy: 
The most stable branch, it is updated approximately once per month and only with significant testing and changes that pass the Improvement Criteria
### staging: 
The most up-to-date branch, it is where feature branches are added to and is what gets merged into deploy. This version of the pipeline has not been as thoroughly tested as deploy, meaning there may be issues/less accurate results.

## Contributing through GitHub
We appreciate all contributions to m2g,
but those accepted fastest will follow a workflow similar to the following:

1. **Comment on an existing issue or open a new issue referencing your addition.**<br />
  This allows other members of the m2g development team to confirm that you aren't
  overlapping with work that's currently underway and that everyone is on the same page
  with the goal of the work you're going to carry out.
  
2. **Fork the m2g repository to your profile.**

3. **Make the changes you've discussed, following the m2g Code Format**
  Keep the changes focused: Changing one feature or addressing one bug per pull request.
  Keep the commit history clean and concise. Commit messages should be in [imperative mood](https://chris.beams.io/posts/git-commit/).
  It is highly recommended that you test your changes thoroughly before submitting a pull request.
  
4. **Make sure your branch is up-to-date**
  If you need to resolve merge conflicts, do so and make sure your branch still runs. Don't ever revert code that you didn't   write to a previous state.

5. **Submit a Pull Request to staging.**
   A member of the development team will review your changes to confirm
   that they can be merged into the main code base

6. **Have your PR reviewed by the development team, and update your changes accordingly in your branch.**
   The reviewers will take special care in assisting you to address their comments, as well as dealing with conflicts
   and other tricky situations that could emerge from distributed development. While your PR may be accepted to staging, it will have to meet the improvement criteria before being added to deploy.

## Improvement Criteria
In order for a change to be made to the m2g deploy branch, it must meet the following criteria:
1. Result in a discriminability value equal to/greater than the current deploy metrics (within noise) on these 5 datasets:
   * BNU1 = 0.927, 1 failures        BNU1_staging = 0.923, 1 failures (113 success)
   * HNU1 = 0.969, 2 failures       HNU1_staging = 0.966, 2 failures (298 success)
   * NKI1 = 0.936, 5 failures       NKI1_staging = 0.924, 4 failures (36 success)
   * NKI24 = 0.937, 5 failures      NKI24_staging = 0.928, 4 failures (36 success)
   * SWU4 = 0.785, 69 failures       SWU4_staging = 0.790, 68 failures (382 success)
   * Settings: `local`, `native`, `csa`, `det`
2. Scans run with 20 seeds at 2mm resolution should finish in less than 1.5 hours
3. There should be no non-python3 dependencies in the pipeline (we only support python3)

## Code formatting
* [Black](https://github.com/ambv/black) for Python
* Automatically apply formatting before commit (either format on save or format on commit)

#### Consider the following naming conventions (Python)
* [PascalCase](http://wiki.c2.com/?PascalCase) for class names
* descriptive_names_with_underscores for function and variable names
* singlename.py for module names
* ALL_CAPS_WITH_UNDERSCORES for constants
* _single_leading_underscore for protected methods / internal functions
* Docstring formatting: [NumPy style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html)

## Issues
* An Issue should consist of a manageable task with a concrete DOD; larger tasks should be split into multiple issues, with milestones, epics, and or tags.

## Testing
* Python: [Pytest](https://doc.pytest.org/)
* Code should have tests at the smallest function size possible (unit tests)
* Every new feature/Pull Request should have tests
* TravisCI integration
    * Each commit/branch/PR
* [Consider test-driven development](https://en.wikipedia.org/wiki/Test-driven_development)

## License
* [Apache Version 2](https://www.apache.org/licenses/LICENSE-2.0.txt)
