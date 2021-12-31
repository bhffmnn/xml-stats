# XML Stats

This script gathers statistics about the elements in an XML file and writes them to a json file.

Output format:

```
{
  tagName: {
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
        "min": number,
        "max": number
      }
    ]
  },
  tagName: {
    ...
}
```
