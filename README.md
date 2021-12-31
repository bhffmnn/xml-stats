# XML Stats

This script gathers statistics about the elements in an XML file and writes them to a json file.

Output format:

```
[
  "tag": string
  "stats": {
    "attributes": [
      {
        "name": string,
        "always": boolean
      }
    ],
    "maxChildrenCount": number,
    "minChildrenCount": number,
    "children": [
      {
        "tag": string,
        "minCount": number,
        "maxCount": number
      }
    ]
  },
  ...
]
```
