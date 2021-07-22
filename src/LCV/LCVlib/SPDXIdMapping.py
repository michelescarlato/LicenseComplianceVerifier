#!/usr/bin/python
# import urllib.request
import requests
import json
import time
import sys
import pandas as pd
import numpy as np
import re
import csv

'''
* SPDX-FileCopyrightText: 2021 Michele Scarlato <michele.scarlato@endocode.com>
*
* SPDX-License-Identifier: MIT
'''

licenses = ["AFL","AGPL","Apache","Artistic","BSD","BSL","bzip2","CC0","CDDL","CPL","curl","EFL","EPL","EUPL","FTL","GPL","HPND","IBM","ICU","IJG","IPL","ISC",
"LGPL","Libpng","libtiff","MirOS","MIT","CMU","MPL","MS","NBPL","NTP","OpenSSL","OSL","Python","Qhull","RPL","SunPro","Unicode","UPL","WTFPL","X11","XFree86","Zlib","zlib-acknowledgement"]
versions = ["1.0","1.0.5","1.0.6","1.1","1.2","1.5","2.0","2.1","3.0","3.1","1","2","3","4","5"]


def CSV_to_dataframe(CSVfilePath, column_names_list):
    """
    Import a CSV and transform it into a pandas dataframe selecting only the useful columns from the Compatibility Matrix
    """
    df = pd.read_csv(CSVfilePath, usecols=column_names_list)
    return df

def IsInAliases(single_verbose_license):
    CSVfilePath = "../../csv/spdx-id.csv"
    IsInAliases = False
    with open(CSVfilePath, 'rt') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if single_verbose_license == row[0]: # if the username shall be on column 3 (-> index 2)
                print (single_verbose_license+" is a recognized Alias")
                IsInAliases = True
                return IsInAliases
        if not IsInAliases:
            print (single_verbose_license+" is a not recognized Alias")
            return IsInAliases

def StaticMapping(single_verbose_license):
    #1540 entries
    CSVfilePath = "../../csv/spdx-id.csv"
    column_names_list = ['Scancode', 'SPDX-ID']
    df = CSV_to_dataframe(CSVfilePath, column_names_list)
    df = df.set_index('Scancode')
    #IsAnAlias = False
    # @Michele you should insert a check upon the column of "scancode name",
    # if the license is there, enter the cycle
    # if not, run the Dynamic Method. <--- this is done in ConvertToSPDX function
    ##########################################################
    # After the dynamic method, a keyerror should be handled
    # you should provide an output without producing a KeyError <--- still should be handled
    single_verbose_license_SPDX_id = df.loc[single_verbose_license]['SPDX-ID']
    if single_verbose_license_SPDX_id is not np.nan:
        return single_verbose_license_SPDX_id
    else:
        return single_verbose_license

def IsAnSPDX(license_name):
    IsSPDX = False
    with open('../../csv/SPDX_license_name.csv', 'rt') as f:
         reader = csv.reader(f)
         for row in reader:
              for field in row:
                  if field == license_name:
                      IsSPDX = True
                      return IsSPDX


def ConvertToSPDX(verbose_license):
    IsAnAlias = False
    IsAnAlias = IsInAliases(verbose_license)
    # if verbose license is within aliases - run static mapping
    if IsAnAlias:
        license = StaticMapping(verbose_license)
        # IF license IS An SPDX ID
        IsSPDX = IsAnSPDX(license)
        if IsSPDX :
            print(license+" is an SPDX-id")
            return license
    # if verbose license IS NOT within aliases - run dynamic mapping
    else:
        license_names = []
        license_name = DynamicMapping(verbose_license)
        #print("After dynamicMapping in ConvertToSPDX")
        print("Dynamic mapping result: ")
        print(license_name)
        IsAnAlias = IsInAliases(license_name)
        if IsAnAlias:
            print(license_name)
            license_mapped = StaticMapping(license_name)
            IsSPDX = IsAnSPDX(license_mapped)
            if IsSPDX :
                print(license_mapped+" is an SPDX-id")
                return license_mapped
        else:
            return license_name


def StaticMappingList(InboundLicenses_cleaned):
    print(InboundLicenses_cleaned)
    CSVfilePath = "../../csv/spdx-id.csv"
    InboundLicenses_SPDX = []
    column_names_list = ['Scancode', 'SPDX-ID']
    df = CSV_to_dataframe(CSVfilePath, column_names_list)
    df = df.set_index('Scancode')
    for license in InboundLicenses_cleaned:
        newElement = df.loc[license]['SPDX-ID']
        if newElement is not np.nan:
            InboundLicenses_SPDX.append(newElement)
        else:
            InboundLicenses_SPDX.append(license)
    return InboundLicenses_SPDX


def DetectWithAcronyms(verbose_license):
    licenseVersion = None
    licenseName = None
    supposedLicense = None
    only=False
    orLater=False

    list_of_words = verbose_license.split()
    for word in list_of_words:
        if word in licenses:
            licenseName=word
        if word in versions:
            licenseVersion=word
            if licenseVersion == "1" or "2" or "3" or "4" or "5":
                licenseVersion=str(float(licenseVersion))
        if word.lower() == "later":
            orLater=True
        if word.lower() == "only":
            only=True
    if licenseName is not None and licenseVersion is None:
        supposedLicense = licenseName
    if not orLater and not only:
        if licenseName and licenseVersion is not None:
            supposedLicense = licenseName+" "+licenseVersion
    if orLater:
        if licenseName and licenseVersion is not None:
            supposedLicense = licenseName+" "+licenseVersion+" or later"
    if only:
        if licenseName and licenseVersion is not None:
            supposedLicense = licenseName+" "+licenseVersion+" only"
    if supposedLicense is not None:
        return supposedLicense
    else:
        return verbose_license

def DetectWithKeywords(verbose_license):
    # probably you could declare globally this variable - inasmuch it is also used by the DetectWithAcronyms() function
    licenseVersion = None
    licenseName = None
    supposedLicense = None
    orLater = False
    only = False
    DynamicMappingKeywordsList=[
        "2010","academic","affero","attribution","berkeley","bsd","bzip","cmu","commons","creative","commons","database","distribution","eclipse","epl","eupl","european",
        "exception","general","ibm","later","lesser","libpng","license","miros","mozilla","mpl,""ntp","only","openssl","patent","python","png","power","powerpc","public","permissive","qhull",
        "reciprocal","software","tiff","uc","universal","upl","zlib","zero"]

    MappedKeywords=[]
    list_of_words = verbose_license.split()
    #check with keywords
    for word in list_of_words:
        if word.lower() in DynamicMappingKeywordsList:
            MappedKeywords.append(word.lower())
        if word in versions:
            print(word)
            licenseVersion=str(word)
            if licenseVersion == "1" or "2" or "3" or "4" or "5":
                licenseVersion=str(float(licenseVersion))
            MappedKeywords.append(licenseVersion)
    print("Mapped Keywords:")
    print(MappedKeywords)
    #If there are keywords matched
    if len(MappedKeywords):
        if "later" in MappedKeywords:
            orLater = True
        if "only" in MappedKeywords:
            only = True
        if "academic" in MappedKeywords:
            licenseName = "AFL"
        # this check should consider also 2-1.0.5 ..
        if "bzip" in MappedKeywords or "2010" in MappedKeywords:
            licenseName = "bzip2-1.0.6"
            return licenseName
        if "distribution" in MappedKeywords:
            licenseName = "CDDL"
        if "powerpc" in MappedKeywords or "power" in MappedKeywords:
            licenseName = "IBM-pibs"
        if "tiff" in MappedKeywords:
            licenseName = "libtiff"
        if "miros" in MappedKeywords:
            licenseName = "MirOS"
            return licenseName
        if "cmu" in MappedKeywords:
            licenseName = "MIT-CMU"
            return licenseName
        if "bsd" in MappedKeywords and "patent" in MappedKeywords:
            licenseName = "BSD-2-Clause-Patent"
            return licenseName
        if "bsd" in MappedKeywords and "uc" in MappedKeywords:
            licenseName = "BSD-4-Clause-UC"
            return licenseName
        if "bsd" in MappedKeywords and "database" in MappedKeywords:
            licenseName = "Sleepycat"
            return licenseName
        if "ibm" in MappedKeywords and "public" in MappedKeywords:
            licenseName = "IPL-1.0"
            return licenseName
        if "libpng" in MappedKeywords and not "zlib" in MappedKeywords and licenseVersion is None:
            licenseName = "Libpng"
        if "libpng" in MappedKeywords and licenseVersion == "2.0":
            licenseName = "libpng-2.0"
            return licenseName
        if "eclipse" in MappedKeywords and licenseVersion == "1.0":
            licenseName = "EPL-1.0"
            return licenseName
        if "eclipse" in MappedKeywords and licenseVersion == "2.0":
            licenseName = "EPL-2.0"
            return licenseName
        if "libpng" in MappedKeywords and "zlib" in MappedKeywords:
            licenseName = "Zlib"

        if "european" in MappedKeywords and licenseVersion == "1.0":
            licenseName = "EUPL-1.0"
            return licenseName
        if "european" in MappedKeywords and licenseVersion == "1.1":
            licenseName = "EUPL-1.1"
            return licenseName
        if "european" in MappedKeywords and licenseVersion == "1.2":
            licenseName = "EUPL-1.2"
            return licenseName
        if "mozilla" in MappedKeywords and licenseVersion == "1.0":
            licenseName = "MPL-1.0"
            return licenseName
        if "mozilla" in MappedKeywords and licenseVersion == "1.1":
            licenseName = "MPL-1.1"
            return licenseName
        if "mozilla" in MappedKeywords and licenseVersion == "2.0" and exception not in MappedKeywords:
            licenseName = "MPL-2.0"
            return licenseName
        if "mozilla" in MappedKeywords and "exception" in MappedKeywords and licenseVersion == "2.0":
            licenseName = "MPL-2.0-no-copyleft-exception"
            return licenseName
        if "sleepycat" in MappedKeywords:
            licenseName = "Sleepycat"
            return licenseName
        if "ntp" in MappedKeywords and "attribution" in MappedKeywords:
            licenseName = "NTP-0"
            return licenseName
        if "ntp" in MappedKeywords and "attribution" not in MappedKeywords:
            licenseName = "NTP"
            return licenseName
        if "upl" in MappedKeywords:
            licenseName = "UPL-1.0"
            return licenseName
        if "universal" in MappedKeywords and "permissive" in MappedKeywords:
            licenseName = "UPL-1.0"
            return licenseName
        if "creative" in MappedKeywords and "commons" in MappedKeywords and "universal" in MappedKeywords:
            licenseName = "CC0-1.0"
            return licenseName
        if "creative" in MappedKeywords and "zero" in MappedKeywords in MappedKeywords:
            licenseName = "CC0-1.0"
            return licenseName
        if "python" in MappedKeywords and "software" in MappedKeywords:
            licenseName = "PSF-2.0"
            return licenseName
        if "python" in MappedKeywords and licenseVersion == "2.0" and "software" not in MappedKeywords:
            licenseName = "Python-2.0"
            return licenseName
        if "openssl" in MappedKeywords:
            licenseName = "OpenSSL"
            return licenseName
        if "qhull" in MappedKeywords:
            licenseName = "Qhull"
            return licenseName
        if "reciprocal" in MappedKeywords and "public" in MappedKeywords and "license" in MappedKeywords:
            if licenseVersion == "1.5":
                licenseName = "RPL-1.5"
                return licenseName
            if licenseVersion == "1.1":
                licenseName = "RPL-1.1"
                return licenseName
        #if "reciprocal" in MappedKeywords and "public" in MappedKeywords and "license" in MappedKeywords:

        if "affero" in MappedKeywords:
            licenseName = "AGPL"
        if "lesser" in MappedKeywords:
            licenseName = "LGPL"
        if "general" in MappedKeywords and "affero" not in MappedKeywords and "lesser" not in MappedKeywords:
            licenseName = "GPL"
    print("License Version")
    print(licenseVersion)
    if licenseName is not None and licenseVersion is None:
        supposedLicense = licenseName
    # check if is or later or only, if not, just assign license name and license version
    if not orLater and not only:
        if licenseName and licenseVersion is not None:
            supposedLicense = licenseName+" "+licenseVersion
    if orLater:
        if licenseName and licenseVersion is not None:
            supposedLicense = licenseName+" "+licenseVersion+" or later"
    if only:
        if licenseName and licenseVersion is not None:
            supposedLicense = licenseName+" "+licenseVersion+" only"
    if supposedLicense is not None:
        return supposedLicense
    else:
        return verbose_license


def DynamicMapping(verbose_license):
    detectedWithAcronymsLicense = DetectWithAcronyms(verbose_license)
    IsSPDX = IsAnSPDX(detectedWithAcronymsLicense)

    if IsSPDX :
        print(detectedWithAcronymsLicense+" is an SPDX-id")
        return detectedWithAcronymsLicense
    IsAnAlias = IsInAliases(detectedWithAcronymsLicense)
    if IsAnAlias:
        print(detectedWithAcronymsLicense)
        detectedWithAcronymsLicense = StaticMapping(detectedWithAcronymsLicense)
        IsSPDX = IsAnSPDX(detectedWithAcronymsLicense)
        if IsSPDX :
            print(detectedWithAcronymsLicense+" is an SPDX-id")
            return detectedWithAcronymsLicense

    detectedWithKeywordsLicense = DetectWithKeywords(verbose_license)
    IsSPDX = IsAnSPDX(detectedWithKeywordsLicense)
    if IsSPDX :
      print(detectedWithKeywordsLicense+" is an SPDX-id")
      return detectedWithKeywordsLicense
    IsAnAlias = IsInAliases(detectedWithKeywordsLicense)
    if IsAnAlias:
      print(detectedWithKeywordsLicense)
      detectedWithKeywordsLicense = StaticMapping(detectedWithKeywordsLicense)
      IsSPDX = IsAnSPDX(detectedWithKeywordsLicense)
      if IsSPDX :
          print(detectedWithKeywordsLicense+" is an SPDX-id")
          return detectedWithKeywordsLicense
    if not IsAnAlias:
        return verbose_license

'''
def DynamicMapping_old(verbose_license):
    licenseVersion = None
    licenseName = None
    supposedLicenseSPDX = None
    supposedLicense = None

    academic=False
    affero=False
    attribution=False
    bsd=False
    bzip=False
    cmu=False
    commons=False
    creative=False
    database=False
    distribution=False
    eclipse=False
    european=False
    exception=False
    general=False
    ibm=False
    IsAnAlias=False
    IsSPDX=False
    lesser=False
    libpng=False
    license=False
    miros=False
    mozilla=False
    ntp=False
    only=False
    openssl=False
    orLater=False
    patent=False
    permissive=False
    powerpc=False
    public=False
    python=False
    qhull=False
    reciprocal=False
    sleepycat=False
    software=False
    tiff=False
    uc=False
    universal=False
    upl=False
    zero=False
    zlib=False


    list_of_words = verbose_license.split()
    for word in list_of_words:
        if word in licenses:
            licenseName=word
        if word in versions:
            licenseVersion=word
            if licenseVersion == "1" or "2" or "3" or "4" or "5":
                print("License version:")
                licenseVersion=str(float(licenseVersion))
                print(licenseVersion)

        if word.lower() == "later":
            orLater=True
        if word.lower() == "only":
            only=True
        if word.lower() == "affero":
            affero=True
        if word.lower() == "lesser":
            lesser=True
        if word.lower() == "general":
            general=True
        if word.lower() == "academic":
            academic=True
        if word.lower() == "distribution":
            distribution=True
        if word == "2010":
            bzip=True
        if word.lower() == "powerpc" or word.lower() == "power":
            powerpc=True
        if word.lower() == "tiff":
            tiff=True
        if word.lower() == "miros":
            miros=True
        if word.lower() == "cmu":
            cmu=True
        # maybe you can add Berkeley?
        if word.lower() == "bsd" or word.lower() == "berkeley":
            bsd=True
        if word.lower() == "database":
            database=True
        if word.lower() == "patent":
            patent=True
        if word.lower() == "uc":
            uc=True
        if word.lower() == "ibm":
            ibm=True
        if word.lower() == "public":
            public=True
        if word.lower() == "libpng" or word.lower() == "png":
            libpng=True
        if word.lower() == "zlib":
            zlib=True
        if word.lower() == "eclipse" or word.lower() == "epl":
            eclipse=True
        if word.lower() == "european" or word.lower() == "eupl":
            european=True
        if word.lower() == "mozilla" or word.lower() == "mpl":
            mozilla=True
        if word.lower() == "exception":
            exception=True
        if word.lower() == "sleepycat":
            exception=True
        if word.lower() == "ntp":
            ntp=True
        if word.lower() == "attribution":
            attribution=True
        if word.lower() == "upl":
            upl=True
        if word.lower() == "permissive":
            permissive=True
        if word.lower() == "universal":
            universal=True
        if word.lower() == "creative":
            creative=True
        if word.lower() == "commons":
            commons=True
        if word.lower() == "zero":
            zero=True
        if word.lower() == "openssl":
            openssl=True
        if word.lower() == "python":
            python=True
        if word.lower() == "software":
            software=True
        if word.lower() == "qhull":
            qhull=True
        if word.lower() == "license":
            license=True
        if word.lower() == "reciprocal":
            reciprocal=True

    # after scanning the whole verbose license try to assign spdx-id.
    if academic:
        licenseName = "AFL"
    if bzip:
        licenseName = "bzip2-1.0.6"
    if distribution:
        licenseName = "CDDL"
    if powerpc:
        licenseName = "IBM-pibs"
    if tiff:
        licenseName = "libtiff"
    if miros:
        licenseName = "MirOS"
        return licenseName
    if cmu:
        licenseName = "MIT-CMU"
        return licenseName
    if bsd and patent:
        licenseName = "BSD-2-Clause-Patent"
        return licenseName
    if bsd and uc:
        licenseName = "BSD-4-Clause-UC"
        return licenseName
    if bsd and database:
        licenseName = "Sleepycat"
        return licenseName
    if ibm and public:
        licenseName = "IPL-1.0"
        return licenseName
    if libpng and not zlib and licenseVersion is None:
        licenseName = "Libpng"
    if libpng and licenseVersion == "2.0":
        licenseName = "libpng-2.0"
        return licenseName
    if eclipse and licenseVersion == "1.0":
        licenseName = "EPL-1.0"
        return licenseName
    if eclipse and licenseVersion == "2.0":
        licenseName = "EPL-2.0"
        return licenseName
    if libpng and zlib:
        licenseName = "Zlib"

    if european and licenseVersion == "1.0":
        licenseName = "EUPL-1.0"
        return licenseName
    if european and licenseVersion == "1.1":
        licenseName = "EUPL-1.1"
        return licenseName
    if european and licenseVersion == "1.2":
        licenseName = "EUPL-1.2"
        return licenseName
    if mozilla and licenseVersion == "1.0":
        licenseName = "MPL-1.0"
        return licenseName
    if mozilla and licenseVersion == "1.1":
        licenseName = "MPL-1.1"
        return licenseName
    if mozilla and licenseVersion == "2.0" and not exception:
        licenseName = "MPL-2.0"
        return licenseName
    if mozilla and licenseVersion == "2.0" and exception:
        licenseName = "MPL-2.0-no-copyleft-exception"
        return licenseName
    if sleepycat:
        licenseName = "Sleepycat"
        return licenseName
    if ntp and attribution:
        licenseName = "NTP-0"
        return licenseName
    if ntp and not attribution:
        licenseName = "NTP"
        return licenseName
    if upl:
        licenseName = "UPL-1.0"
        return licenseName
    if universal and permissive:
        licenseName = "UPL-1.0"
        return licenseName
    if creative and commons and universal:
        licenseName = "CC0-1.0"
        return licenseName
    if creative and zero:
        licenseName = "CC0-1.0"
        return licenseName
    if python and software:
        licenseName = "PSF-2.0"
        return licenseName
    if python and licenseVersion == "2.0" and not software:
        licenseName = "Python-2.0"
        return licenseName
    if openssl:
        licenseName = "OpenSSL"
        return licenseName
    if qhull:
        licenseName = "Qhull"
        return licenseName
    if reciprocal and public and license and licenseVersion == "1.5":
        licenseName = "RPL-1.5"
        return licenseName
    if reciprocal and public and license and licenseVersion == "1.1":
        licenseName = "RPL-1.1"
        return licenseName

    if affero:
        licenseName = "AGPL"
    if lesser:
        licenseName = "LGPL"
    if general and not affero and not lesser:
        licenseName = "GPL"
    if licenseName is not None and licenseVersion is None:
        supposedLicense = licenseName
        supposedLicenseSPDX = licenseName
    if not orLater and not only:
        if licenseName and licenseVersion is not None:
            supposedLicense = licenseName+" "+licenseVersion
            #supposedLicenseSPDX = licenseName+"-"+licenseVersion
    if orLater:
        if licenseName and licenseVersion is not None:
            supposedLicense = licenseName+" "+licenseVersion+" or later"
            #supposedLicenseSPDX = licenseName+"-"+licenseVersion+"-or-later"
    if only:
        if licenseName and licenseVersion is not None:
            supposedLicense = licenseName+" "+licenseVersion+" only"
            #supposedLicenseSPDX = licenseName+"-"+licenseVersion+"-only"
    if supposedLicense is not None:
        print("Supposed license:")
        print(supposedLicense)
        IsAnAlias = IsInAliases(supposedLicense)
    #if supposedLicenseSPDX is not None:
        IsSPDX = IsAnSPDX(supposedLicense)
    # the next three if could be simply the else of the last if - currently debugging
    if IsAnAlias: #and IsSPDX:
        return supposedLicense#,supposedLicenseSPDX
    #if IsAnAlias and not IsSPDX:
        #return supposedLicense,supposedLicenseSPDX
    if IsSPDX:
        return supposedLicense
    if not IsAnAlias:# and IsSPDX:
        return verbose_license#supposedLicense,supposedLicenseSPDX
    #if not IsAnAlias and not IsSPDX:
        #print("enters here")
        #return verbose_license,supposedLicenseSPDX
'''
