import json
import sys
import socket

def main():

    # check number of command line arguments
    if len(sys.argv) != 4:
        print("incorrect number of arguments")
        sys.exit()

    INPUT_PATH = sys.argv[1]
    OUTPUT_PATH = sys.argv[2]
    CANVAS = sys.argv[3]

    # open and parse input json
    with open(INPUT_PATH, 'r') as in_file:
        in_json = json.load(in_file)

    # create dictionary to store output
    out_json = {}

    # store the context, id, and type
    out_json["@context"] = "http://iiif.io/api/presentation/2/context.json"
    out_json["@id"] = "https://islandora.traefik.me/" + OUTPUT_PATH
    out_json["@type"] = "sc:AnnotationList"

    # create list to store the annotations
    resources_list = []

    # get the contents, height, width and the x-y coordinates of the top left corner of the bounding box
    for page in in_json["fullTextAnnotation"]["pages"]:
        for block in page["blocks"]:
            if block["blockType"] != "TEXT":
                continue
            
            for paragraph in block["paragraphs"]:
                vertices = paragraph["boundingBox"]["vertices"]

                # get coordinates of the top left corner of the bounding box
                x0, y0 = vertices[0].get("x"), vertices[0].get("y")
                # get coordinates of the bottom right corner of the bounding box
                x2, y2 = vertices[2].get("x"), vertices[2].get("y")

                # calculate width and height of bounding box
                width = x2 - x0
                height = y2 - y0

                # get the content
                content = ""
                words = paragraph["words"]

                for word in words:
                    for symbol in word["symbols"]:
                        content += symbol["text"]

                        # add a space between words if break detected
                        if "property" in symbol and symbol["property"]["detectedBreak"]["type"] == "SPACE":
                            content += " "
                
                # bind to any free port
                sock = socket.socket()
                sock.bind(('', 0))

                # add the information retrieved to the resources dictionary
                resources = {}
                resources["@id"] = "http://localhost:" + str(sock.getsockname()[1]) + "/annotation/" + str(hash(json.dumps(paragraph, sort_keys=True)))
                resources["@type"] = "oa:Annotation"
                resources["@context"] = "http://iiif.io/api/presentation/2/context.json"
                resources["on"] = CANVAS + "#xywh=" + str(x0) + "," + str(y0) + "," + str(width) + "," + str(height)
                resources["label"] = content
                
                res = {}
                res["@type"] = "dctypes:Text"
                res["http://dev.llgc.org.uk/sas/full_text"] = content
                res["format"] = "text/html"
                res["chars"] = "<p>" + content + "</p>"

                resources["resource"] = res
                resources["motivation"] = ["oa:commenting"]

                resources_list.append(resources)

    out_json["resources"] = resources_list

    # store extracted data in the output file
    try:
        with open(OUTPUT_PATH, 'w') as out_file:
            json.dump(out_json, out_file)
    except Exception as e:
        print(e)

    print("done")

if __name__ == '__main__':
    main()
