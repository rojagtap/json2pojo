# json2pojo
A simple utility for translating json (responses) into plain old java objects (POJOs)

### Requirements:
1. python 3.x
2. dateutil, install using `pip install python-dateutil`

### How to use:
1. Clone the repo and `cd` into the project root directory
2. run `python convert.py <path to the json file> <name of the pojo class (defaults to POJO)>`
3. copy the output from the command line

### Notes:
1. The tool expects json content in a file because the terminal is not very good at handling json strings (I'll soon add support for **properly escaped** json strings).
2. This tool assumes Jackson as your json serializer/deserializer in java and adds the `@JsonProperty` annotation for mapping the json to the pojo.
