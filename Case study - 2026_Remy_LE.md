# Step 1 \- Strategic plan

Objective: Double qualified demo pipeline from 8–10 to 16–20/month within 90 days  
**1\. Diagnosis: Why the 1% Reply Rate Happened**

* likely not due to volume, but poor targeting, enrichment quality and weak personalization context.

**2\. ICP (Hyper) Definition**

"data teams in European scale-ups" is too vague. We want to be more specific:

* **Title**: Head of Data, Data Engineering Manager, CDO, VP Analytics (decision makers related to data)  
* **Stage**: Series A–C, 50–500 employees, raised in last 18 months (budget available)  
* **Geography**: France, Germany, Netherlands, UK \- GDPR-heavy markets \= stronger data governance need  
* **Hiring signals**: Active job postings for Data Engineers or Analytics Engineers \= data team scaling \= governance needed  
* **Company signals**: using modern data tech stack like Snowflake, Databricks (job postings, LinkedIn tech stack signals)  
* reacts/comments on posts about data governance, etc. *(this part was not implemented due to price constraints)*  
* reacts/comments on posts from Northstar’s competitors (ex: “comment to get X”) *(this part was not implemented due to price constraints)*  
* **Lead scoring** to prioritize leads 

ex: “Jean Dupont, Head of Data of a scale-up in France, 180 employees, raised 3 months ago, using Snowflake, hiring analytics engineers, likely increasing data governance complexity; opener angle: growing data team \+ governance overhead.

**3\. Negative filters (exclusions):**

* Pre-seed / bootstrap (no budget / no priority)  
* 500 employees (enterprise sales cycle, wrong motion)  
* B2C companies (lower data governance regulatory pressure)  
* Competitors' customers (detected via job postings mentioning competing tools)

**4\. Success metrics**

Target: reply rate \>3-5% (vs \<1% baseline), 20+ qualified demos/month (vs 8-10), within 90 days.

# Step 2 \- Functional build

**Build link:** [https://app.clay.com/shared-table/share\_0tf8uleNqj7Nwb5P7hg](https://app.clay.com/shared-table/share_0tf8uleNqj7Nwb5P7hg)

**Stack choices:** 

- Clay (free trial) for data enrichment  
- Python fallback (in case no more free clay credits for demonstration), [JavaScript dashboard](https://claude.ai/public/artifacts/e5b6442c-94ce-4bb4-990e-2827da1db8b9) built with Claude as backup to display the output list of leads (mock implementation, no real API used) \-\> [https://github.com/Remy-Le/breega\_case\_study](https://github.com/Remy-Le/breega_case_study) pour plus d’info

**Reason for the choice :** 

- Clay: Waterfall layer \-\> multiple sources to verify data, free trial was enough for the case study  
- Python: free (+ API costs if implemented), version 1 was generated with Claude in one shot (didn’t have time to improve it based on the case study’s time constraints) so I still added it in the case study as fallback

Con: Clay can be a bit expensive if we do lots of enrichment, though it is still \< 600€ (Northstar’s budget)

**Why not Apollo (free plan):**

- sometimes data is outdated  
- Since we didn’t have good results with Apollo, I wanted to use another data enrichment tool and see if it’s better.

# Step 3 \- Loom

[https://www.loom.com/share/d24a36bdbd18477b9901398fc03eefd1](https://www.loom.com/share/d24a36bdbd18477b9901398fc03eefd1)  
