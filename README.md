# MasterProjectSonarQube
Author: Caroline Graebel

## Table of Contents
- [Data](#data)
	- [Data Source](#data-source)
	- [Licensing](#licensing)
	- [Merging the data from the two database versions](#merging)

<a name="data"></a>
## Data

<a name="data-source"></a>
### Data Source
All projects are sourced from [The Technical Debt Dataset](https://doi.org/10.1145/3345629.3345630). The data contains SonarQube analysis data for multiple Github projects. All projects fulfill the following requirements:
* Developed in Java
* Older than three years
* More than 500 commits
* More than 100 classes
* Usage of Jira issue tracking systems with at least 100 issues

<a name="licensing"></a>
### Licensing
The Technical Debt Dataset is used in this project for research purposes and therefore follows the licensing guidelines given by the creators [(README: Chapter License)](https://github.com/clowee/The-Technical-Debt-Dataset).

<a name="project-selection"></a>
### Project Selection
There are two versions of the Technical Dataset published on Github. It is stated that for version 2 some new projects are in the database while others have been removed [(Technical Dataset Github Release Notes)](https://github.com/clowee/The-Technical-Debt-Dataset/releases). To maximise data, projects from the first version of the database that haven't been updated in the second version are used along the new and updated projects from version 2.

<a name="merging"></a>
### Merging the data from the two database versions
To combine the data from the two versions of the Technical Debt Dataset, it is necessary to align the naming conventions of the variable. For version 1, the variables are in camel case (exampleVariable). For version 2, the variables are in snake case with uppercase letters (EXAMPLE_VARIABLE). Since we want to concatenate the two dataframes, it is important that the variables match. Furthermore, version 2 provides more variables than version 1, with version 1 being a subset of the variables provided by version 2. This might be of interest later, since there will be missing values for these variables for the version 1 data. <br>
Through regex transformation, version 1 variable names are changed into snake case with uppercase letters and the two dataframes are concatenated.