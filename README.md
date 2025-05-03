# MasterProjectSonarQube
Author: Caroline Graebel

## Table of Contents
- [Data](#data)
	- [Data Source](#data-source)
	- [Licensing](#licensing)
	- [Project Selection](#project-selection)
	- [Cleaning the Tags in SonarQube Issues](#cleaning-issues)
	- [Merging the data from the two database versions](#merging)
	- [Removing duplicated analysis](#removing-duplicates)
	- [Variable Selection based on missingness](#handle-missingness)
- [Analysing the relationship between code smells and other variables](#analysis)
	- [Correlation Analysis](#correlation-analysis)
		- [Correlations between all numerical variables](#correlation-between-all)
		- [Correlations between amount of code smells and metrics](#correlation-between-cs-nums)

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

<a name="cleaning-issues"></a>
### Cleaning the Tags in SonarQube Issues
To prepare the data for the model, only issues that are code smells are selected. Only columns needed to identify the analysis, tags and issue messages are selected. <br>
Version 1 doesn't contain a tag column, only version 2 provides information on what tags are associated with the code smell issues. However, the issue message can be in most cases consistently assigned to a set of tags. An exception are messages that are very rare. This makes it possible to infer issue tags for version 1 for the issue messages that are known from version 2. For this, the messages are cleaned off specifics, like concrete variable names or counts. For version 2, there are 390 unique messages after cleaning. When extracting unique tag and message pairs, there are 393 pairs, showing that the pairing of messages and tags is almost completely consistent. Investigated exceptions either have missing tags or contain a subset of tags ("convention" vs "convention,psr2"). When cleaning the messages for version 1 and investigating the intersection between version 1 and version 2 messages, it could be shown that 268/340 unique messages of version 1 are contained in version 2 as well. Furthermore, messages that are not directly contained in version 2 still can be assigned to consistent tags by using a striking substring of the message. Only for some substrings, there are no tags connected at all. Given the strong consistency, for 99.98% of version 1 tags can be inferred by using the issue message. <br>
For version 2, unique tags for each analysis are extracted and saved.

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
As a result, for some variables there is a small amount of missing data. For the variable FUNCTION_COMPLEXITY_DISTRIBUTION there are 9875 missing values, which is a lot but doesn't justify an outright removal of the variable. <br>
The final resulting dataframe contains 62 columns.

<a name="handle-statics"></a>
### Dropping numerical variables with static values
When investigating the correlation of variables, there are some variables that can't be correlated. Through investigation it can be shown that some metrics only contain static values over all rows (0). When training a model, metrics that only contain a static value doesn't provide meaningful information (variance) to the learning process. Therefore, they are getting removed. <br>
The resulting dataframe contains 53 columns.

<a name="analysis"></a>
## Analysing the relationship between code smells and other variables
To gain further insights on a sensible modelling approach, the relationship between code smells and other metrics needs to be understood.

<a name="correlation-analysis"></a>
### Correlation Analysis
Since most variables (including amount of code smells) are numerical, a regression approach might be sensible. For this, it is useful to know which variables correlate and therefore might be good predictors.

<a name="correlation-between-all"></a>
#### Correlations between all numerical variables
Plotting a correlation matrix for all numerical variables in the dataset reveals that there are a lot of static columns in the dataset. These are removed. <br>
For the remaining columns, a lot of metrics correlate postively and strongly with each other. Only the technical debt measurement variables SQALE_DEBT_RATIO and NEW_SQALE_DEBT_RATIO and COMMENT_LINES_DENSITY correlate little to negatively with most metrics.

<a name="correlation-between-cs-nums"></a>
#### Correlations between amount of code smells and metrics
When plotting the correlations between the amount of code smells and other metrics specifically, it shows that code smells has a very strong positive correlation to most of the metrics, with only the technical debt measures and COMMENT_LINE_DENSITY correlating little or strongly negatively. The amount of code smells might be predictable through a simple regression model.
