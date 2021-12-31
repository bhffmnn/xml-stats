import json
import xml.sax


# Settings
root_tag = "name-of-root-tag"
string_tag = "str" # Tag name used internally for strings. Has to be a tag name 
                   # that's not being used in the XML file
source_path = "source.xml" # Path to XML file
target_path = "target.json" # Target file path

def find(condition, iterable):
    for element in iterable:
        if condition(element):
            return element
    return None

class XmlStatsHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.elementStack = []
        self.statsList = []

        
    def startElement(self, tag, attributes):
        if tag != root_tag:
            newElement = { "tag": tag, "attributes": attributes.getNames(), "children": [] }
            
            if len(self.elementStack) > 0:
                self.elementStack[-1]["children"].append(newElement)

            self.elementStack.append(newElement)


    def endElement(self, tag):
        if tag != root_tag:
            element = self.elementStack.pop()
            statsElement = find(lambda e: e["tag"] == tag, self.statsList)
            # NEW
            if not statsElement:
                attributesStats = []
                for attr in element["attributes"]:
                    attributesStats.append({"name": attr, "always": True})

                maxChildrenCount = len(element["children"])

                childrenStats = []
                for child in element["children"]:
                    tagCount = len(list(filter(lambda c: c["tag"] == child["tag"], element["children"])))
                    childStats = {"tag": child["tag"], "minCount": tagCount, "maxCount": tagCount}
                    childrenStats.append(childStats)

                self.statsList.append({"tag": tag, "stats": {"attributes": attributesStats, "maxChildrenCount": maxChildrenCount, "minChildrenCount": maxChildrenCount, "children": childrenStats}})
            
            # UPDATE
            else:
                # Update attributesStats                
                attributesStats = map(lambda a: a["name"], statsElement["stats"]["attributes"])
                # Add new attributes
                for attr in element["attributes"]:
                    if attr not in attributesStats:
                        statsElement["stats"]["attributes"].append({"name": attr, "always": False})
                # Update 'always' property
                for attrName in attributesStats:
                    if attrName not in element["attributes"]:
                        find(lambda a: a["name"] == attrName, statsElement["stats"]["attributes"])["always"] = False
                
                childrenStats = statsElement["stats"]["children"]

                # Update max and min children count
                if statsElement["stats"]["maxChildrenCount"] < len(element["children"]):
                    statsElement["stats"].update({"maxChildrenCount": len(element["children"])})
                if statsElement["stats"]["minChildrenCount"] > len(element["children"]):
                    statsElement["stats"].update({"minChildrenCount": len(element["children"])})

                # Update childrenStats
                # Increase max count / add child
                for child in element["children"]:
                        tagCount = len(list(filter(lambda c: c["tag"] == child["tag"], element["children"])))
                        childElementStats = find(lambda c: c["tag"] == child["tag"], childrenStats)
                        # EXISTS => increase max count if necessary
                        if childElementStats:
                            if childElementStats["maxCount"] < tagCount:
                                childElementStats["maxCount"] = tagCount
                        # NONE => NEW
                        else:
                            childStats = {"tag": child["tag"], "minCount": 0, "maxCount": tagCount}
                            childrenStats.append(childStats)
                # Decrease min count
                existingChildTags = list(map(lambda c: c["tag"], childrenStats))
                currentChildTags = list(map(lambda c: c["tag"], element["children"]))
                for childTag in existingChildTags:
                    if childTag not in currentChildTags:
                        find(lambda c: c["tag"] == childTag, childrenStats)["minCount"] = 0


    def characters(self, content):
        # This is a safeguard. In theory this should never be 0
        if len(self.elementStack) > 0:
            currentElementChildren = self.elementStack[-1]["children"]
            # This causes subsequent strings to be ignored
            if len(currentElementChildren) == 0 or not currentElementChildren[-1]["tag"] == string_tag:
                currentElementChildren.append({ "tag": string_tag, "attributes": [], "children": [] })


if __name__ == "__main__":
    handler = XmlStatsHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    parser.parse(open(source_path, "r", encoding="utf8"))
    json_dump = json.dumps(handler.statsList, ensure_ascii=False, indent=2)
    f = open(target_path, "w", encoding="utf8")
    f.write(json_dump)
    f.close()
