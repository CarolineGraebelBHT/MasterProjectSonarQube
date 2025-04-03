# MasterProjectSonarQube
Author: Caroline Graebel

## Data

### Data Source
All projects are sourced from [The Technical Debt Dataset](https://doi.org/10.1145/3345629.3345630). The data contains SonarQube analysis data for multiple Github projects. All projects fulfill the following requirements:
* Developed in Java
* Older than three years
* More than 500 commits
* More than 100 classes
* Usage of Jira issue tracking systems with at least 100 issues

### Licensing
The Technical Debt Dataset is used in this project for research purposes and therefore follows the licensing guidelines given by the creators [(README: Chapter License)](https://github.com/clowee/The-Technical-Debt-Dataset).

### Project Selection
There are two versions of the Technical Dataset published on Github. It is stated that for version 2 some new projects are in the database while others have been removed [(Technical Dataset Github Release Notes)](https://github.com/clowee/The-Technical-Debt-Dataset/releases). To maximise data, projects from the first version of the database that haven't been updated in the second version are used along the new and updated projects from version 2.