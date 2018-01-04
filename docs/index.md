# Consumer Complaint Database search API

This API provides programmatic search access to the CFPB's [database of consumer complaints](https://www.consumerfinance.gov/data-research/consumer-complaints/).  
Search results can be returned in json, csv, xls, or xlsx formats.

Details on its use can be found [here](documentation/index.html).

#### Notes

The database generally updates daily, and contains certain information for each complaint, including the source of the complaint, the date of submission, and the company the complaint was sent to for response. The database also includes information about the actions taken by the company in response to the complaint, such as, whether the company’s response was timely and how the company responded. If the consumer opts to share it and after we take steps to remove personal information, we publish the consumer’s description of what happened. Companies also have the option to select a public response. Company level information should be considered in context of company size and/or market share. Complaints referred to other regulators, such as complaints about depository institutions with less than $10 billion in assets, are not published in the Consumer Complaint Database.
