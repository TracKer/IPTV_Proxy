# Author: Timmy93
# URL: https://github.com/Timmy93/M3uParser
# Modified

import os
import re
import urllib.request
import random


class M3uParser:

    def __init__(self, logging):
        self.files = []
        self.logging = logging

    # Download the file from the given url
    def downloadM3u(self, url, filename):
        currentDir = os.path.dirname(os.path.realpath(__file__))
        if not filename:
            filename = "test.m3u"
        try:
            filename = os.path.join(currentDir, filename)
            urllib.request.urlretrieve(url, filename)
        except:
            print("Cannot download anything from the url\nHave you modified the ini file?")
            exit()
        self.readM3u(filename)

    # Read the file from the given path
    def readM3u(self, filename):
        self.filename = filename
        self.readAllLines()
        self.parseFile()

    # Read all file lines
    def readAllLines(self):
        self.lines = [line.rstrip('\n') for line in open(self.filename, encoding='utf-8')]
        return len(self.lines)

    def parseFile(self):
        numLine = len(self.lines)
        for n in range(numLine):
            line = self.lines[n]
            if line[0] == "#":
                # print("Letto carattere interessante")
                self.manageLine(n)

    def manageLine(self, n):
        lineInfo = self.lines[n]
        lineLink = self.lines[n + 1]
        if lineInfo != "#EXTM3U":
            paramTemplate = (
                ("tvg-name", "tvg-name=\"(.*?)\"", 1),
                ("tvg-ID", "tvg-ID=\"(.*?)\"", 1),
                ("tvg-logo", "tvg-logo=\"(.*?)\"", 1),
                ("group-title", "group-title=\"(.*?)\"", 1),
                ("title", "[,](?!.*[,])(.*?)$", 1),
            )

            values = {
                "titleFile": os.path.basename(lineLink),
                "link": lineLink,
            }

            for item in paramTemplate:
                m = re.search(item[1], lineInfo)
                if m is None:
                    continue
                value = m.group(item[2])
                values[item[0]] = value

            self.files.append(values)

    def exportJson(self):
        # TODO
        print("Not implemented")

    # Remove files with a certain file extension
    def filterOutFilesEndingWith(self, extension):
        self.files = list(filter(lambda file: not file["titleFile"].endswith(extension), self.files))

    # Select only files with a certain file extension
    def filterInFilesEndingWith(self, extension):
        # Use the extension as list
        if not isinstance(extension, list):
            extension = [extension]
        if not len(extension):
            self.logging.info("No filter in based on extensions")
            return
        new = []
        # Iterate over all files and extensions
        for file in self.files:
            for ext in extension:
                if file["titleFile"].endswith(ext):
                    # Allowed extension - go to next file
                    new.append(file)
                    break
        self.logging.info("Filter in based on extension: [" + ",".join(extension) + "]")
        self.files = new

    # Remove files that contains a certain filterWord
    def filterOutFilesOfGroupsContaining(self, filterWord):
        self.files = list(filter(lambda file: filterWord not in file["tvg-group"], self.files))

    # Select only files that contais a certain filterWord
    def filterInFilesOfGroupsContaining(self, filterWord):
        # Use the filter words as list
        if not isinstance(filterWord, list):
            filterWord = [filterWord]
        if not len(filterWord):
            self.logging.info("No filter in based on groups")
            return
        new = []
        for file in self.files:
            for fw in filterWord:
                if fw in file["tvg-group"]:
                    # Allowed extension - go to next file
                    new.append(file)
                    break
        self.logging.info("Filter in based on groups: [" + ",".join(filterWord) + "]")
        self.files = new

    # Getter for the list
    def getList(self):
        return self.files

    # Return the info assciated to a certain file name
    def getCustomTitle(self, originalName):
        result = list(filter(lambda file: file["titleFile"] == originalName, self.files))
        if len(result):
            return result
        else:
            print("No file corresponding to: " + originalName)

    # Return a random element
    def getFile(self, randomShuffle):
        if randomShuffle:
            random.shuffle(self.files)
        if not len(self.files):
            self.logging.error("No files in the array, cannot extract anything")
            return None
        return self.files.pop()
