#!/usr/bin/env python

"""

Latest.py Generate latest_platform.json file for Cohorte website.
It contains Urls of the last snapshots.

:author: Bassem Debbabi

..

    Copyright 2015 isandlaTech

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

# Module version
__version_info__ = (0, 0, 1)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

import json
import optparse
import sys
import os
import xml2json

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

DEV_REPO_URL = "http://repo.isandlatech.com/maven/snapshots/org/cohorte/platforms/cohorte"
RELEASE_REPO_URL = "http://repo.isandlatech.com/maven/releases/org/cohorte/platforms/cohorte"
MAVEN_FILE = "maven-metadata.xml"

def get_file_path(url_path, json_data, dist_name, what):       
    snapshots = json_data["metadata"]["versioning"]["snapshotVersions"]["snapshotVersion"]
    artifact_id = json_data["metadata"]["artifactId"]
    if what == "changelog":
        elem = (item for item in snapshots 
                            if item["extension"] == "txt" 
                            and item["classifier"] == "changelog").next()
        if elem is not None:
            return url_path + "/" + artifact_id + "-" + elem["value"] + "-" + "changelog.txt"
        else:            
            return None      
    elif what == "version":
        suffix = "-distribution-version"
        extension = ".js"
    elif what == "dist":
        suffix = "-distribution"
        extension = ".tar.gz"                  
                            
    elem = (item for item in snapshots 
                            if item["extension"] != "pom" 
                            and item["classifier"] == dist_name + suffix).next()
    if elem is not None:
        return url_path + "/" + artifact_id + "-" + elem["value"] + "-" + dist_name + suffix + extension
    else:
        return None        

def main():
    p = optparse.OptionParser(
        description='Converts Maven metadata XML file to Cohorte Website latest.json JSON file.',
        prog='latest',
        usage='%prog -o file.json [url]'
    )
    p.add_option('--out', '-o', help="Write to OUT instead of stdout")
    p.add_option('--version', '-v', help="Cohorte Version")
    
    
    options, arguments = p.parse_args()

    if options.version:
        version = options.version
        if options.version.endswith("SNAPSHOT"):            
            url_path = DEV_REPO_URL + "/" + version 
            stage = "dev"            
        else:
            url_path = RELEASE_REPO_URL + "/" + version 
            stage = "release"
    else:
        print("which cohorte's version? e.g. 1.0.1-SNAPSHOT")

    print(url_path)
    if stage == "dev":    	    
        fp = urllib2.urlopen(url_path + "/" +  MAVEN_FILE)
        input = fp.read()
        options.pretty = True
        out = xml2json.xml2json(input, options, 1, 1)
        # generate cohorte file
        json_data = json.loads(out)
    
    json_final_file = {}
            	
    def add_dist(dist_name):
        json_final_file["cohorte-"+dist_name+"-distribution"] = {}
    
        if stage == "dev":
            version_file_path = get_file_path(url_path, json_data, dist_name, "version")
            changelog_file_path = get_file_path(url_path, json_data, dist_name, "changelog")
            dist_file_path = get_file_path(url_path, json_data, dist_name, "dist")
        else:
            version_file_path = url_path + "/cohorte-" + version + "-" + dist_name + "-distribution-version.js"
            changelog_file_path = url_path + "/cohorte-" + version + "-" + "changelog.txt"
            dist_file_path = url_path + "/cohorte-" + version + "-" + dist_name + "-distribution.tar.gz"
                    
        try:
            version_file_stream = urllib2.urlopen(version_file_path)
            version_file = version_file_stream.read()    
            version_json = json.loads(version_file)
            json_final_file["cohorte-"+dist_name+"-distribution"]["version"] = version_json["version"]
            json_final_file["cohorte-"+dist_name+"-distribution"]["stage"] = version_json["stage"]
            json_final_file["cohorte-"+dist_name+"-distribution"]["timestamp"] = version_json["timestamp"] 
            json_final_file["cohorte-"+dist_name+"-distribution"]["changelog"] = changelog_file_path
            json_final_file["cohorte-"+dist_name+"-distribution"]["files"] = { "tar.gz" : dist_file_path}
        except:
            json_final_file["cohorte-"+dist_name+"-distribution"]["version"] = ""
            json_final_file["cohorte-"+dist_name+"-distribution"]["stage"] = ""
            json_final_file["cohorte-"+dist_name+"-distribution"]["timestamp"] = ""                
            json_final_file["cohorte-"+dist_name+"-distribution"]["changelog"] = ""
            json_final_file["cohorte-"+dist_name+"-distribution"]["files"] = { "tar.gz" : ""}
        
    add_dist("python")
    add_dist("macosx")
    add_dist("linux")
    add_dist("windows")
                
    if (options.out):
        file = open(options.out, 'w')
        file.write(json.dumps(json_final_file, sort_keys=True, indent=2, separators=(',', ': ')))
        file.close()
    else:
        print(out)    

if __name__ == "__main__":
    main()


