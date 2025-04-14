# MasterProjectSonarQube
Author: Caroline Graebel

## Table of Contents
- [Data](#data)
	- [Data Source](#data-source)
	- [Licensing](#licensing)
	- [Merging the data from the two database versions](#merging)
	- [Removing duplicated analysis](#removing-duplicates)
	- [Variable Selection based on missingness](#handle-missingness)

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
Through regex transformation, version 1 variable names are changed into snake case with uppercase letters and the two dataframes are concatenated. <br>
When merging the two dataframes, it becomes apparent that there is no time variable contained for version 2 of the database. Since the analysis have a temporal dependence on each other, it is useful for modelling purposes to keep the time of the analysis. The time can be matched through the variable ANALYSIS_KEY version 2 provides, that links to a meta information table in the database from which the timestamp can be extracted. After matching the timestamps with the analysis key, the concatenated table now has timestamps for the analysis also for version 2.

<a name="removing-duplicates"></a>
### Removing duplicated analysis
Over the two different database versions, there are duplicated analysis. The dataset before removing duplicates has 144640 rows. An analysis is a duplicate when there are two analysis for the same project at the same point of time. When removing duplicates with pandas by that logic, 144262 rows remain. However, the date format is inconsistent over the two databases (for example: "2014-07-23 18:17:17" and "2014-07-23T18:17:17Z"). When adapting the date strings to follow the format YYYY-MM-DD HH:MM:SS just like the first example string and dropping duplicates, 140748 rows remain.

<a name="handle-missingness"></a>
### Variable Selection based on missingness
The dataframe has 140748 rows after removing duplicated analysis but still provides 244 columns. The columns so far contain a lot of identifier variables that can be linked to other tables in the database for further information. The most variables are different metrics. It has been stated before that version 1 contains less variables than version 2, with version 1 being a subset of the version 2 variables. To see which of the variables are useful for modelling, information density needs to be assessed. This can be done by looking at the portion of missing values. When doing that, it can be seen that for a lot of the variables there are all or almost all values missing for a big portion of the variables. <br>
A first filter that is worth applying to filter out variables that provide no value due to the missingness is deleting all variables where more than 140000 values are missing. By doing that, only 65 columns remain. <br>
There are more columns where missingness occurs based on the version of the database the analysis is coming from. Most of them are identifier variables which can be removed since the only identifier needed for modelling is the name of the project. <br>
For one variable, a typing error in the database leads to a mismatch when merging the two dataframes.  In one version, the variable NEW_SQALE_DEBT_RATIO is called NEW_SQALE_DEBT_RATION. The wrongly written column is removed and the contained values are written into NEW_SQALE_DEBT_RATIO. <br>
As a result, for some variables there is a small amount of missing data. For the variable FUNCTION_COMPLEXITY_DISTRIBUTION there are 9875 missing values, which is a lot but doesn't justify an outright removal of the variable.