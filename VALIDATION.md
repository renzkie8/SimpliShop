# Portfolio validation

- Python source files that parsed successfully: 1.
- Python source files with existing syntax issues: 0.
- Notebook documents parsed and checked for cleared outputs: 0.
- Required portfolio documentation and ignore rules checked.
- Publication files checked for provider-token patterns, the original student identifier and embedded database credential URIs.
- No publication file exceeds GitHub’s 100 MB per-file limit.

## Scope

Source parsing is not execution or a complete correctness test. Notebook code cells can contain Jupyter magics and were not executed. The initial portfolio audit did not execute applications. Follow-up local smoke checks are described below. Model training, live external API calls and website deployment were not performed. Java compilation was not run because a JDK was not available in this environment. Third-party licensing and historical benchmark claims were not independently verified.

## Follow-up restoration checks

Application and dependency files were compared with the pre-portfolio GitHub commit. The only retained source difference is the student-ID privacy placeholder in the introductory CCCS exercise.

- simplishop: passed. PASS: HTML served; health reports disconnected database; invalid signup input rejected. Azure SQL, real login/signup and deployment not tested.

These checks used isolated copies and disposable databases. Full GUI workflows, live weather and Azure SQL operations remain unverified.
