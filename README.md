# MasterProjectSonarQube
Author: Caroline Graebel

## Table of Contents
- [Data](#data)
	- [Data Source](#data-source)
	- [Licensing](#licensing)
	- [Project Selection](#project-selection)
	- [Merging the data from the two database versions](#merging)
	- [Removing duplicated analysis](#removing-duplicates)
	- [Variable Selection based on missingness](#handle-missingness)
	- [Cleaning the Tags in SonarQube Issues](#cleaning-issues)
	- [Merging Tags with Metrics](#tags-metrics-merge)
- [Analysis](#analysis)
	- [Correlation Analysis between Code Smells and other variables](#correlation-analysis)
		- [Correlations between all numerical variables](#correlation-between-all)
		- [Correlations between amount of code smells and metrics](#correlation-between-cs-nums)
	- [Analysing Tags](#tags-analysis)
		- [Missingness of Tags](#tags-missing)
		- [Distribution of Tags for version 2](#tags-distribution2)
		- [Distribution of Tags for version 1](#tags-distribution1)
		- [Distribution of Tags for versions 1 and 2 combined]((tags-distribution1+2)
	- [Analysing the number of issues per commit and duplicated issues](#num-issues-duplis)
		- [Connection between a commit and the numbers of issues](#num-issues-per-commit)
		- [Investigating the repetition of issues over different analysis](#duplication-analysis)
	- [Analysing the data for predicting code smell tags](#tags-model-analysis)
		- [Distribution of projects](#project-distribution)
		- [Distribution of tags](#tags-distribution-model)
		- [Time Analysis per project)(#time-analysis)
- [Models](#models)
	- [Predicting the amount of Code Smells](#code-smell-prediction)
		- [Data preparation for models](#data-prep-cs)
		- [Fitting models to predict the amount of Code Smells](#fitting-models-cs)
			- [Multiple Linear Regression](#mlr-cs)
			- [Generalised Additive Model](#gam-cs)
			- [Projection Pursuit Regression](#ppr-cs)
			- [XGBoost](#xgboost-cs)
			- [Support Vector Machine](#svm-cs)
		- [Results](#results-cs)
	-[Predicting the tags of new Code Smells](#tag-prediction]

<a name="data"></a>
## Data

<a name="data-source"></a>
### Data Source
The project data originates from [The Technical Debt Dataset](https://doi.org/10.1145/3345629.3345630), which contains SonarQube analysis data for multiple GitHub projects. The selection criteria for these projects included:
* Developed in Java
* Older than three years
* More than 500 commits
* More than 100 classes
* Usage of Jira issue tracking systems with at least 100 issues

<a name="licensing"></a>
### Licensing
This research project adheres to the licensing guidelines provided by the creators of The Technical Debt Dataset, as detailed in the [(README: Chapter License)](https://github.com/clowee/The-Technical-Debt-Dataset).

<a name="project-selection"></a>
### Project Selection
The analysis leverages two versions of The Technical Debt Dataset available on GitHub. Version 2 incorporates new projects and removes some existing ones, as outlined in the [(Technical Dataset Github Release Notes)](https://github.com/clowee/The-Technical-Debt-Dataset/releases). To maximise the dataset, projects unique to the first version were combined with the updated and new projects from the second version.

<a name="merging"></a>
### Merging the data from the two database versions
To combine the data from the two versions of the Technical Debt Dataset, it is necessary to align the naming conventions of the variable. For version 1, the variables are in camel case (exampleVariable). For version 2, the variables are in snake case with uppercase letters (EXAMPLE_VARIABLE). Since we want to concatenate the two dataframes, it is important that the variables match. Furthermore, version 2 provides more variables than version 1, with version 1 being a subset of the variables provided by version 2. This might be of interest later, since there will be missing values for these variables for the version 1 data. <br>
Through regex transformation, version 1 variable names are changed into snake case with uppercase letters and the two dataframes are concatenated. <br>
When merging the two dataframes, it becomes apparent that there is no time variable contained for version 2 of the database. Since the analysis have a temporal dependence on each other, it is useful for modelling purposes to keep the time of the analysis. The time can be matched through the variable ANALYSIS_KEY version 2 provides, that links to a meta information table in the database from which the timestamp can be extracted. After matching the timestamps with the analysis key, the concatenated table now has timestamps for the analysis also for version 2.

<a name="removing-duplicates"></a>
### Removing duplicated analysis
The combined dataset initially contained 144,640 rows. Duplicates, defined as analyses for the same project at the same time, were removed. Inconsistent date formats (e.g., "2014-07-23 18:17:17" vs. "2014-07-23T18:17:17Z") were standardized to "YYYY-MM-DD HH:MM:SS" before duplicate removal, resulting in a final dataset of 140,748 rows.

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

<a name="cleaning-issues"></a>
### Cleaning the Tags in SonarQube Issues
To prepare the data for the model, only issues that are code smells are selected. Only columns needed to identify the analysis, tags and issue messages are selected. <br>
Version 1 doesn't contain a tag column, only version 2 provides information on what tags are associated with the code smell issues. However, the issue message can be in most cases consistently assigned to a set of tags. An exception are messages that are very rare. This makes it possible to infer issue tags for version 1 for the issue messages that are known from version 2. For this, the messages are cleaned off specifics, like concrete variable names or counts. For version 2, there are 390 unique messages after cleaning. When extracting unique tag and message pairs, there are 393 pairs, showing that the pairing of messages and tags is almost completely consistent. Investigated exceptions either have missing tags or contain a subset of tags ("convention" vs "convention,psr2"). When cleaning the messages for version 1 and investigating the intersection between version 1 and version 2 messages, it could be shown that 268/340 unique messages of version 1 are contained in version 2 as well. Furthermore, messages that are not directly contained in version 2 still can be assigned to consistent tags by using a striking substring of the message. Only for some substrings, there are no tags connected at all. Given the strong consistency, for 99.98% of version 1 tags can be inferred by using the issue message. <br>
For version 2, unique tags for each analysis are extracted and saved. <br>
Tags are generated for version 1. For this, a mapping table is created that contains the original processed issue messages of version 1 combined with tags from version 2 that align with the processed messages. This mapping then is used to assign the tags to the appropriate messages based on the original messages that are also contained in the original issue data of version 1. Tags could be assigned to all open issues which are used for modelling.

<a name="tags-metrics-merge"></a>
### Merging Tags with Metrics
The goal of merging the tags with their according analysis metrics is to create a dataset to be used for modelling e tags of new code smell issues through the analysis metrics. To bring together the metrics with the tags of the code smell issues detected in that analysis, three different data sources are needed. The combined metrics of database version 1 and 2, containing the necessary identifier columns (ANALYSIS_KEY and COMMIT_HASH) to join them with the issue tags. The tags belonging to the analysis are split by database version. For version 1, the dataframe contains the projectID, the creationCommitHash and the uniqueTags assigned to the new code smells per analysis. For version 2, instead of creationCommitHash there is ANALYSIS_KEY to link the tags to the metrics. <br>
The tags data is merged with the metrics in two steps, leading to a table of the same size with two different tags columns TAGS_x and TAGS_y (for each version). Both columns don't overlap on any analysis. To bring the tags columns together, first the tags of database 1 are copied into a column TAGS. For each missing value in that column, tags of version 2 are filled where present. <br>
Next, a subset of variables is selected. The subset contains the software metrics, the tags, the COMMIT_HASH, ANALYSIS_KEY and PROJECT_ID for identification and the SQ_ANALYSIS_DATE to track the time series. The complete list of variables contained in the subset is:
* 'PROJECT_ID'
* 'SQ_ANALYSIS_DATE'
* 'COMMIT_HASH'
* 'ANALYSIS_KEY'
* 'CLASSES'
* 'FILES'
* 'LINES'
* 'NCLOC'
* 'PACKAGE'
* 'STATEMENTS'
* 'FUNCTIONS'
* 'COMMENT_LINES'
* 'COMPLEXITY'
* 'CLASS_COMPLEXITY'
* 'FUNCTION_COMPLEXITY'
* 'COGNITIVE_COMPLEXITY'
* 'LINES_TO_COVER'
* 'UNCOVERED_LINES'
* 'DUPLICATED_LINES'
* 'DUPLICATED_BLOCKS'
* 'DUPLICATED_FILES'
* 'COMMENT_LINES_DENSITY'
* 'DUPLICATED_LINES_DENSITY'
* 'TAGS'
The resulting dataframe is deduplicated but as expected there are no duplicates. The identifier columns COMMIT_HASH and ANALYSIS_KEY are dropped. <br>
Next, only those rows are kept in which there is a value for TAGS. After this, only 17775 / 140748 observations remain. <br>
The tags are filtered. Some tags are flags for violeted rule sets which describe an array of issues and not one specifically. These ruleset-tags are: 'cert', 'cwe', 'misra', 'psr2' and 'code-smell'. Tags which describe a specific issue and are built-in are used. Also tags, where the name is the literal meaning is kept, such as 'redundant' and 'obsolete'. Tags which occur less than a 100 times are considered the tail of the distribution and removed. After this selection, the remaining tags are: 'error-handling', 'convention', 'suspicious', 'pitfall', 'brain-overload', 'unused', 'bad-practice', 'clumsy', 'antipattern', 'redundant', 'performance', 'obsolete' and 'confusing'. <br>
Based on this, the TAGS values are now cleaned so they only contain the selected tags. Rows which don't contain any tags after this ([]) are removed (596 rows).

<a name="analysis"></a>
## Analysis

<a name="correlation-analysis"></a>
### Correlation Analysis
To inform the modeling approach, the relationships between code smells and other metrics are examined. <br>
Since most variables (including amount of code smells) are numerical, a regression approach might be sensible. For this, it is useful to know which variables correlate and therefore might be good predictors.

<a name="correlation-between-all"></a>
#### Correlations between all numerical variables
Plotting a correlation matrix for all numerical variables in the dataset reveals that there are a lot of static columns in the dataset. These are removed. <br>
For the remaining columns, a lot of metrics correlate postively and strongly with each other. Only the technical debt measurement variables SQALE_DEBT_RATIO and NEW_SQALE_DEBT_RATIO and COMMENT_LINES_DENSITY correlate little to negatively with most metrics.

<a name="correlation-between-cs-nums"></a>
#### Correlations between amount of code smells and metrics
When plotting the correlations between the amount of code smells and other metrics specifically, it shows that code smells has a very strong positive correlation to most of the metrics, with only the technical debt measures and COMMENT_LINE_DENSITY correlating little or strongly negatively. The amount of code smells might be predictable through a simple regression model.

<a name="tags-analysis"></a>
### Analysing Tags
For using tags as a label, it's important to know their missingness and their distribution. Version 2 comes with tags assigned, for version 1 they are generated. First, version 2 is investigated for the amount of missing tags globally and per project. Then, the distribution of tags is analysed. This is done for version 1 as well. The goal is to understand which tags are useful for modelling. Lastly, the distribution of tags when taking together both versions is investigated.

<a name="tags-missing"></a>
#### Missingness of Tags
Over all ~1 million rows containing code smells and open issues,  23697 rows have missing tags. This equals 0.11% of all data. <br>
When investigating missingness by project, it can be shown that there are some projects for which a lot of the tags are missing. For Santuario and Digester, over 50% of tags are missing. Only for two thirds of the projects there are missing values at all.

<a name="tags-distribution2"></a>
#### Distribution of Tags for version 2
To count tags, the tags are generalised per analysis. One analysis can find multiple code smell issues that have multiple tags. Tags are generalised through counting only the unique tags occuring for one analysis. When plotting the resulting distribution of generalised tags, a bit over half of the tags occuring in the data are well represented, ranging from 1-12% occurence. The rest are rarely used and probably can't be meaningfully used for modelling. <br>
Furthermore, CERT, CWE and MISRA tags are given for the violation of rule sets that describe a coding standard violation rather than a specific issue ([SonarQube Tag Documentation](https://docs.sonarsource.com/sonarqube-server/9.8/user-guide/rules/built-in-rule-tags/)). These should be removed, as they don't describe a concrete type of code smell. 

<a name="tags-distribution1"></a>
#### Distribution of Tags for version 1
The analysis is done similarly to version 2. The distribution is similar, with some tags having different positions ordered by occurence. The tail is also not as long as in version 2, as only 26 out of 31 tags appear. Most tags also have an occurence of 1-12% in the data.

<a name="tags-distribution1+2"></a>
#### Distribution of Tags for versions 1 and 2 combined
When putting together the tag counts of version 1 and 2, all tags are represented. Only the most common variables have significantly been increased by adding version 1 and 2 together. 

<a name="num-issues-duplis"></a>
### Analysing the number of issues per commit and duplicated issues
In the version 1 data, each issue is defined by the ID of the commit it got introduced in and (if solved) which commit fixed the issue. For version 2, an analysis key is given to each issue that links it to the commit over another table. It is to be investigated whether the two data versions both display a link to the introducing commit by investigating how the metrics of the analysis link to the issues. It is expected that each issue is linked to one commit and therefore analysis. <br>
Another investigation is necessary to understand whether known code smells are repeatedly found and noted for each commit or whether already identified errors are listed again for each analysis or not. The expectation is that known issues aren't repeatedly listed if already identified. <br>
The investigation is done only for the smallest  project in the dataset, Apache Commons Daemon (version 1: commons-daemon, version 2: org.apache:daemon), to make the results comprehensible by eye.

<a name="num-issues-per-commit"></a>
#### Connection between a commit and the numbers of issues
For version 1, when joining the metrics to the issues over the commit hash it could be shown that each commit indead has one or multiple issues. <br>
For version 2, when joining the metrics and issue table over the analysis key, it could be shown that similar to version 1, each commit has one or multiple issues. <br>
For both versions, there are some commits that introduce a lot more issues than others, with the Apache Commons Daemon project introducing max. 348 issues with one commit opposed to mostly issue amounts smaller than ten in version 1, and max. 45 issues for version 2. It might be challenging to predict all the tags associated with such issue heavy commit. Therefore, not only the distribution of tags should be reconsidered when cutting out observations but also the amount of issues detected in it.

<a name="duplication-analysis"></a>
#### Investigating the repetition of issues over different analysis
To expose duplications, identifier columns are dropped and duplicates are extracted. <br>
For version 1, there are 5 out of 393 issues that are duplicates. All duplicates describe fixed issues. Therefore, there are 0 open duplicated issues in the version 1 data. <br>
For version 2, there are 7 duplications for 796 issues. Importantly, these 7 duplications are open issues. There are no clues to hint at a systematic occurence. It is more probable, that the few duplicated errors are reintroduced errors over different commits. <br>
As a result, it could be confirmed that issues only get tracked once in the commits they got introduced.

<a name="#tags-model-analysis"></a>
### Analysing the data for predicting code smell tags
For the subset of data selected for predicting code smell tags, distribution of projects and tags are investigated. Lastly, a visualisation for timestamps in the data per project is created to better understand how even the analysis are spread over time.

<a name="#project-distribution"></a>
#### Distribution of projects
The representations of projects in the dataset is very uneven, with hive being strongly represented ith over 1750 analysis. Most projects have between 250 and 750 analysis. For some projects there are around 150 or less analysis. Also, not all projects have their issues represented in the dataset. Only 38/39 projects are represented in the data.

<a name="#tags-distribution-model"></a>
#### Distribution of tags
Most tags are properly represented, appearing between 2500 and 6000 times in the data. 'redundant', 'performance', 'obsolete', and 'confusing' only appear around or less than a 1000 times in the data. The rarest one is 'confusing' with only 523 appearences.

<a name="#time-analysis"></a>
#### Time Analysis per project
When plotting all projects on a timeline, the distance between analysis is inconsistent for most projects. Some have been analysed regularly over a timeframe. There are also projects that have a long history, but for some, they have only been developed shortly. It can't be known whether gaps in the analysis really equal a lack of information more than a change in coding prioritisation, holidays of developers etc.. For most analysis, they still should strongly depend on prior commits.

<a name="models"></a>
## Models
To investigate whether models are able to predict code smells in models, two perspectives are explored. <br>
The first approach is to predict the amount of code smells that are expected in each commit by the software metrics. It is also of interest to understand which software metrics are most helpful in predicting the amount of code smells successfully. <br>
For the second approach, the unique tags of new code smells per commit are predicted by software metrics. Again it is investigated what metrics are most useful for this task.

<a name="code-smell-prediction"></a>
## Predicting the amount of Code Smells
For predicting how many code smells are to be expected in a commit depending on the software metrics measured by SonarQube, different models are fitted and compared to find an option that succeeds at predicting the amount of code smells the best. <br>
Since correlation analysis showed that the amount of code smells correlates highly with a lot of metrics, a simple linear regression model is tried. Furthermore, a generalised additive model is chosen for its ability to model the relationship between the label and each predictor individually. Projection pursuit regression is used to explore whether a dimension reduction is useful for a better model performance. XGBoost is used for its generally strong performance and ability to handle missing values. Lastly, a support vector machine is used for it's flexibility.

<a name="data-prep-cs"></a>
### Data preparation for models
To ensure that all models run on the same quality of data, the data import is streamlined. For this, a python script is used that contains multiple functions. <br>
The load_df-function reads in the cleaned data from the directory it is saved in. <br>
The function put_label_in_front() puts the label (in this context CODE_SMELLS) in the first column of the dataframe. This makes it easier to check, whether the following scaling has been done properly. <br>
The select_variables-function takes a list of variables that should contain all variables to be used for modelling (label and predictors). The dataframe then gets subsetted to only contain those variables and returned. <br>
The scale_predictors-function scales all numerical variables contained in the subsetted dataframe to be centered (having a mean of 0) and having a standard deviation of 1. <br>
All models are passed the same selection of variables and the same label. <br>
The predictors that describe software metrics are the following:
* CLASSES,
* FILES
* LINES
* NCLOC
* PACKAGE
* STATEMENTS
* FUNCTIONS
* COMMENT_LINES
* COMPLEXITY
* CLASS_COMPLEXITY
* FUNCTION_COMPLEXITY
* COGNITIVE_COMPLEXITY
* LINES_TO_COVER
* UNCOVERED_LINES
* DUPLICATED_LINES
* DUPLICATED_BLOCKS
* DUPLICATED_FILES
* COMMENT_LINES_DENSITY
* DUPLICATED_LINES_DENSITY <br>
The label is CODE_SMELLS. <br>
The data containing the data for all projects over all commits has missing values in 29 of the 140748 rows. Since this is such a small share, the rows are omitted all but one model instead of applying a method to fill the missing values. Since XGBoost is able to learn paths for missing values, the 29 rows are included in the modelling process.

<a name="fitting-models-cs"></a>
### Fitting models to predict the amount of Code Smells
With the prepared data, each model is now fitted. The train-test-split is 70/30 for each model and is seeded. To evaluate the performance and make the model performance comparable, $`R^2`$, Mean Absolute Error (MAE) and Mean Squared Error (MSE) are calculated on the predictions on the test sets.

<a name="mlr-cs"></a>
#### Multiple Linear Regression
As a first approach, each predictor is used to fit a multiple linear regression model. The resulting model has a high MAE and MSE, with two variables shown to be not significant (alpha = 0.05). The $`R^2`$ is very high, showing that the model does represent a high portion of variance provided by the training data properly. Leaving out the two variables and fitting again results in a worse performance and model fit. <br>
In both cases the model functions return a warning for having a multicollinearity problem. This means that the predictors are strongly correlated to each other which negatively impacts model performance. Multicollinearity can be shown by doing a correlation analysis, which showed high correlations between the metrics. It is also useful to calculate the Variance Inflation Factor (VIF) for each variable to further investigate multicollinearity. A VIF of higher than 10 is considered to indicate strong multicollinearity problems. 13/17 variables are over and significantly over a VIF of 10, showing that multicollinearity indeed is an issue in the data. However, it can be countered by using regularisation. There are ridge and lasso regression as options. However, since removing variables worsened the performance, and lasso regression results in shrinking coefficients to 0, ultimately removing variables from the regression formula, Ridge Regression is chosen instead. <br>
The ridge regression model relies on cross-validation to find the best alpha value regulating the strength of the penalty term. The resulting best model however performs very similarly to the first model without penelisation, showing that multiple linear regression might not be a good choice for the task at hand.

<a name="gam-cs"></a>
#### Generalised additive model
For the GAM, each predictor is fit by using a cubic spline term, resulting in a much improved MAE and MSE compared to the MLR models. The $`R^2`$ is improved. <br>
When changing cubic spline terms into linear terms for variables where the scatterplot of the amount of code smells and the predictor looks very linear, the performance gets worse.

<a name="ppr-cs"></a>
#### Projection Pursuit Regression
Projection Pursuit Regression is a good approach to counter the curse of dimensionality. This can occur when there are a lot of predictors in the data, leading to a high dimensional space, drifting data points more apart. Projection Pursuit Regression projects the data into lower dimensional space (default is 3 dimensions). When fitting the model, the result shows a better performance than both GAM and MLR with a high $`R^2`$.

<a name="xgboost-cs"></a>
#### XGBoost
To create a good XGBoost model, a parameter space is defined that contains multiple options per parameter. Through cross-validated grid search, the combination of parameters that minimises the MAE is chosen. The resulting model shows a very low MAE and MSE, leading to the best test performance of all models.

<a name="#svm-cs"></a>
#### Support Vector Machine
Similar to XGBoost, a parameter grid was defined to optimize the model with cross-validated GridSearch. The resulting model has higher errors compared to all models but Linear Regression. It scores a high $`R^2`$.

<a name="results-cs"></a>
### Results
Out of all the models, XGBoost shows the strongest performance. GAM and PPR show comparable performance. MLR shows the worst performance.