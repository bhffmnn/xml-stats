import json
import xml.sax

skip_tags = ["name-of-root-tag-probably"]
string_tag = "str" # Tag used internally for strings. Should be a name not used in the XML file
source_path = "source.xml" # Path to XML file
target_path = "target.json" # Target file path

class XmlStatsHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.elementStack = []
        self.statsDict = {}

        
    def startElement(self, tag, attributes):
        if tag not in skip_tags:
            newElement = { "tag": tag, "attributes": attributes.getNames(), "children": [] }
            
            if len(self.elementStack) > 0:
                self.elementStack[-1]["children"].append(newElement)

            self.elementStack.append(newElement)


    def endElement(self, tag):
        if tag not in skip_tags:
            element = self.elementStack.pop()
            statsElement = self.statsDict.get(tag)
            
            # NEW
            if statsElement == None:
                attributesStats = []
                for attr in element["attributes"]:
                    attributesStats.append({"name": attr, "always": True})

                maxChildrenCount = len(element["children"])

                childrenStats = []
                for child in element["children"]:
                    tagCount = len(list(filter(lambda c: c["tag"] == child["tag"], element["children"])))
                    childStats = {"tag": child["tag"], "min": tagCount, "max": tagCount}
                    childrenStats.append(childStats)

                self.statsDict.update({tag: {"attributes": attributesStats, "maxChildrenCount": maxChildrenCount, "minChildrenCount": maxChildrenCount, "children": childrenStats}})
            
            # UPDATE
            else:
                # Update attributesStats                
                attributesStats = map(lambda a: a["name"], statsElement["attributes"])
                # Add new attributes
                for attr in element["attributes"]:
                    if attr not in attributesStats:
                        statsElement["attributes"].append({"name": attr, "always": False})
                # Update 'always' property
                for attrName in attributesStats:
                    if attrName not in element["attributes"]:
                        list(filter(lambda a: a["name"] == attrName, statsElement["attributes"]))[0]["always"] = False
                
                childrenStats = statsElement["children"]

                # Update max and min children count
                if statsElement["maxChildrenCount"] < len(element["children"]):
                    statsElement.update({"maxChildrenCount": len(element["children"])})
                if statsElement["minChildrenCount"] > len(element["children"]):
                    statsElement.update({"minChildrenCount": len(element["children"])})

                # Update childrenStats
                # Increase max count / add child
                for child in element["children"]:
                        tagCount = len(list(filter(lambda c: c["tag"] == child["tag"], element["children"])))
                        # This will have length 0 or 1
                        filteredChildElementInfos = list(filter(lambda c: c["tag"] == child["tag"], childrenStats))
                        # LENGTH 1 = EXISTS => increase max count if necessary
                        if len(filteredChildElementInfos) != 0:
                            if filteredChildElementInfos[0]["max"] < tagCount:
                                filteredChildElementInfos[0]["max"] = tagCount
                        # LENGTH 0 = NEW
                        else:
                            childStats = {"tag": child["tag"], "min": 0, "max": tagCount}
                            childrenStats.append(childStats)
                # Decrease min count
                existingChildTags = list(map(lambda c: c["tag"], childrenStats))
                currentChildTags = list(map(lambda c: c["tag"], element["children"]))
                for childTag in existingChildTags:
                    if childTag not in currentChildTags:
                        list(filter(lambda c: c["tag"] == childTag, childrenStats))[0]["min"] = 0


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
    json_dump = json.dumps(handler.statsDict, ensure_ascii=False, indent=2)
    f = open(target_path, "w", encoding="utf8")
    f.write(json_dump)
    f.close()
