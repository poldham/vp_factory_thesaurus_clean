### Objective

Use an ollama model to review the name cluster groupings in this file factory_working_example_group_normalized_30122025.the

The objective is to remove entries that obviously do not belong in the same group based on the content of their names and keep only
those that do belong together.

## Tools

An ollama server is available locally and in the cloud with a range of models and could be used for the review

## Main Cases

We have the following main cases.

- Distinctive names: some names such as dupont, merk, novartis and pfizer or phrases such as proctor and gamble share a distinctive linguistic root and 
can be safely grouped together. They are normally distinctive proper nouns. 
- Generic names: some terms such as development, biotechnology, pharma or pharmaceuticals are generic and may lead to false positive clusters
where the key term that varies is the distinctive term (often a place name such as shanghai or shenzen or other proper noun).
- Incorrect matches: Some names are incorrectly grouped together due to shared generic terms or coincidental similarities.
- US government: The united states government appears frequently but with high diversity in the underlying data and may be expressed as the government of the
united states, the us government commonly with a pattern of the secretary of state. These have been merged to US government in the 
input file
- Universities: There is an important distinction for universities in the united states between state universities and other universities
where the state university of new york (or new york state university) is distinct from new york university.
- Other cases: there may be other cases that arise during the review process.