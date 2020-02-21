#Load the libraries
library(tidyverse)
library(readr)
install.packages("ggthemes")
library(ggthemes)

#Set working directory
setwd("pd")

#Read in summary_df.csv file from the ibdgc_notebook.ipynb
summary_df=read_csv(file = "summary_df.csv")%>%select(-X1)

#Group summary_df by center_id and obtain a count for the different diagnoses
summary_df%>%group_by(center_id)%>%count(diagnosis)%>%mutate(count=n)%>%select(-n)

#Group summary_df by center_id and obtain a count for the different genders
summary_df%>%group_by(center_id)%>%count(gender)%>%mutate(count=n)%>%select(-n)

#Group summary_df by country and obtain a count for the different genders, diagnoses and ibd affection statuses
summary_df%>%group_by(country)%>%count(gender,diagnosis,ibd_affection_status)%>%mutate(count=n)%>%select(-n)

#Graph the different genders, diagnoses and ibd affection statuses for each Country
ggplot(summary_df,aes(diagnosis))+
  geom_bar(aes(fill=gender))+
  facet_wrap(~country)+
  theme_few()+
  coord_flip()
