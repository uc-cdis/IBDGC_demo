# IIBDGC-GWAS-Mega-2 Tutorial

This tutorial will walk a user through signing into the IBDGC commons, using the GraphQL query tool, and how to use that output with Jupyter and R notebooks.

## Logging In To The Commons

To log into the IBDGC commons, please go to the [Home page](https://ibdgc.datacommons.io/) and sign in with your Google account. After a successful login, the user's name will appear in the upper right corner of the commons.

## Using Query

Please start by navigating to the Query page found in the upper right corner of the commons. For these examples, the GraphQL queries will be done using the Graph Model. Clicking the `Switch to Graph Model` button on the right side will select that appropriate model. Once in Graph Model mode, a user can search through the Graph Model nodes as seen on the [Data Dictionary page](https://ibdgc.datacommons.io/DD).

To start, a simple query will be used to illustrate the sections of a GraphQL query:

```GraphQL
{
  project(submitter_id: "IIBDGC-GWAS-Mega-2") {
    centers(first: 5) {
      investigator_name
      id
      participants(first: 3, offset: 4) {
        submitter_id
      }
    }
  }
}
```
This query is looking at the projects and is filtering for the project with the submitter_id equal to `IIBDGC-GWAS-Mega-2`. From that project, the query will pull the information for the first five `center` node entries. In this case, information returned will be the `investigator_name` at the center and the `id` in the Data Model. The query will then pull information for the `participant` node. In this example, only the `submitter_id` will be returned but for the first three entries after an `offset` of four entries.

This example query demonstrates that filtering can be done at any node, and it can either be a filter for a string or numeric placement. It is also important to note that to get information for both `project` and `participant`, the query had to "walk" through the `center` node, as the `center` node is required for that [path](https://ibdgc.datacommons.io/DD).

To avoid long paths, the query can start at any node, which changes the focal point of the query. This will often change the output of the query. It also important to note that this will change the name of the node, as the starting node is always singular, but all subsequent nodes become plural.

```GraphQL
{
  participant(project_id:"IIBDGC-GWAS-Mega-2", first:3, offset:4){
    submitter_id
    centers(first:5){
      investigator_name
      id
    }
  }
}
```

While similar to the previous query, this one will return the first three participants' `submitter_id`, of all participants, offset by four in the project `IIBDGC-GWAS-Mega-2`. It will then display the `investigator_name` and `id` for each of those participants. It will show the first five centers, but this filter does nothing as each participant will only come from one `center`. This example also demonstrates that queries can go in either direction of the Data Model, it is not require that the query starts with the highest level node.

## Tutorial

Before navigating to the `Workspace`, users will need to obtain a `credentials.json` file. This file will be used in the querying of data and it determines what data sets are available to the current user. To obtain this file, navigate to the `Profile` page. Click the `Create API key` and then select the `Download json` option. Save this file locally as it will be uploaded to the user's workspace.

Navigating to the `Workspace` page, this tutorial will start in the Jupyter workspace. Once the Jupyter workspace has loaded, open the `pd/` directory. Import the `credentials.json` file as well as the notebook tutorials into this directory. Any files saved outside of the `pd/` directory will be removed after terminating the workspace.

### Jupyter Notebook

To start the tutorial, select the `ibdgc_notebook.ipynb` notebook. Cell one will run the necessary updates and make sure that all libraries are installed. The second cell will run the code for the function, `ibd.query_summary_counts()`, from the library file `ibdgc_library.py`. This will return the data frame for the projects in the commons.

The following cell will use the `ibd.query_counts_by_collection()` function, from the library file `ibdgc_library.py`, to run the following GraphQL query for the whole project and save it as a data frame.

For this tutorial the project `IIBDGC-GWAS-Mega-2` was chosen, so the resulting code is `summary_df=ibd.query_counts_by_collection("IIBDGC-GWAS-Mega-2")`. Since the project `IIBDGC-GWAS-Mega-2` has a large number of participants, it is too large for a single GraphQL query. To properly query the database, the query needs to be broken into smaller segments. This is done by choosing a `first:1000` and an `offset` equal to the `n*1000` instance, starting at zero, to complete the query. This query will return all participants' `submitter_id`, their `gender`, `diagnosis`, `ibd_affection_status`, and the `center` information for them such as `investigator_name`, `country` and `submitter_id` of the entry. The GraphQL query for this is:

```GraphQL
{
  participant(project_id: "IIBDGC-GWAS-Mega-2", first: 1000,offset:n*1000) {
            submitter_id
            centers {
                investigator_name
                country
                submitter_id
            }
            demographics {gender}
            diagnoses {ibd_affection_status
                diagnosis}}
            }
```

While this function is running an output is generated to show what section is being queried:

```
Obtaining 1000 entities from offset 0 for 57917 entries.
Obtaining 1000 entities from offset 1000 for 57917 entries.
Obtaining 1000 entities from offset 2000 for 57917 entries.
Obtaining 1000 entities from offset 3000 for 57917 entries.
...
```

The next cell will display the data frame. Followed by a cell that saves the data frame to a file and another cell that loads the saved data frame. Writing the data frame to a file will save time, as querying large datasets can be computationally intensive.

Finally the last cell in the Jupyter notebook demonstrates one of the various ways to organize the data within Python:

```Python
summary_df.drop(['country','investigator'],axis=1).groupby(['center_id','gender','diagnosis','ibd_affection_status']).count()
```

To close out of the Jupyter Workspace, select the `Terminate Workspace` button located at the bottom of the browser window.

### R Studio Notebook

Start the R Studio workspace and select the `pd/` directory in the lower right corner pane, under the `Files` tab. Select the file `ibdgc_notebook.R` and then run all the code in order. This will load and install the required libraries for the notebook. It will then set the working directory as the `pd/` directory and load the file from the Jupyter Notebook.

The follow lines of codes demonstrate the different ways the information could be grouped to display count numbers.

```R
#Group summary_df by center_id and obtain a count for the different diagnoses
summary_df%>%group_by(center_id)%>%count(diagnosis)%>%mutate(count=n)%>%select(-n)

#Group summary_df by center_id and obtain a count for the different genders
summary_df%>%group_by(center_id)%>%count(gender)%>%mutate(count=n)%>%select(-n)

#Group summary_df by country and obtain a count for the different genders, diagnoses and ibd affection statuses
summary_df%>%group_by(country)%>%count(gender,diagnosis,ibd_affection_status)%>%mutate(count=n)%>%select(-n)
```

Based on the final transformation of the data, this will graphed using the following code.

```R
#Graph the different genders, diagnoses and ibd affection statuses for each Country
ggplot(summary_df,aes(diagnosis))+
  geom_bar(aes(fill=gender))+
  facet_wrap(~country)+
  theme_few()+
  coord_flip()
```

This will return a figure with stacked bar plots for each diagnosis, differentiating between the recorded genders per Country.
