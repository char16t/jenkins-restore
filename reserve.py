#!/usr/bin/env python

import sys
import argparse
import logging
import urllib2
import base64
import json
import requests
import random
import string
import datetime

def mylog(message):
    """
    Write log message to stdout and  to predefined file
    """
    time = "[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] "
    outmsg = time + message
    print(outmsg)
    with open("not_restored.txt", "a") as myfile:
        myfile.write(outmsg + "\n")

def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    logging.debug("User: %s" % args.user)
    logging.debug("Password: %s" % args.password)
    logging.debug("Config: %s" % args.config)
    logging.debug("Prefix: %s" % args.prefix)
    logging.debug("Jobs: %s" % args.jobs)
    
    lines = [l.strip() for l in args.jobs]
    dataconf = args.config.read()
    for line in lines:
        url = args.prefix + "/" + line + "/config.xml"
        auth = (args.user, args.password)
        headers = {"Content-Type" : "application/xml"}
        r = requests.post(url, auth=auth, data=dataconf, headers=headers)
        st1 = r.status_code
        
        if st1 == 404:
            mylog(line + " is not reserved. Not found")
            continue
        
        r = requests.get(args.prefix + "/" + line + "/api/json", auth=auth, headers=headers)
        #print("URL: " + r.url)
        #print("Text: " + r.text)
        for build in r.json()["builds"]:
            url = args.prefix + "/" + line + "/" + str(build["number"]) + "/doDelete"
            auth = (args.user, args.password)
            headers = {"Content-Type" : "application/xml"}
            r = requests.post(url, auth=auth, headers=headers)
            st1 = r.status_code
            print line + "[" + str(build["number"]) + "] -> " + str(st1)
        
        
        if st1 != 400 and st1 != 500 and st1 != 403:
            disable_url = args.prefix + "/" + line + "/disable"
            r = requests.post(disable_url, auth=auth)
            st2 = r.status_code
            new_name = 'RES_' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)) + "_RESERVE_SDP"
            rename_url = args.prefix + "/" + line + "/doRename?newName=" + new_name
            r = requests.post(rename_url, auth=auth)
            st3 = r.status_code
            if st3 == 400 and st3 == 500 and st3 == 403:
                mylog(line + " is not reserved. Unknown error")
            print line + " -> " + new_name + " (" + str(st1) + "," + str(st2) + "," + str(st3) + ")"
        else:
            delete_url = args.prefix + "/" + line + "/doDelete"
            r = requests.post(delete_url, auth=auth)
            st3 = r.status_code
            if st3 == 200:
                mylog(line + " is not reserved. Deleted")
            else:
                mylog(line + " is not reserved. Unknown error")
            print line + " -> delete (" + str(st3) + ")"
            
        

def make_request(url, username, password):
    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)   
    result = urllib2.urlopen(request)
    data = json.load(result)
    return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Does a thing to some stuff.",
        epilog="As an alternative to the commandline, params can be placed" +
        "in a file, one per line, and specified on the commandline like " +
        "'%(prog)s @params.conf'.",
        fromfile_prefix_chars='@')
    parser.add_argument(
        "-u",
        "--user",
        required=True,
        metavar="user",
        help="Jenkins user")
    parser.add_argument(
        "-p",
        "--password",
        required=True,
        metavar="password",
        help="Jenkins password")
    parser.add_argument(
        "-c",
        "--config",
        metavar="config",
        required=True,
        type=argparse.FileType('r'),
        help="Jenkins CI job configuration")
    parser.add_argument(
        "-r",
        "--prefix",
        metavar="prefix",
        required=True,
        help="Jenkins CI job URL prefix")
    parser.add_argument(
        "-j",
        "--jobs",
        metavar="jobs",
        required=True,
        type=argparse.FileType('r'),
        help="File with Jenkins CI job names")
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true")
    args = parser.parse_args()
    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    main(args, loglevel)
