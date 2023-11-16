import csv

'''
* SPDX-FileCopyrightText: 2023 Michele Scarlato <michele.scarlato@gmail.com>
*
* SPDX-License-Identifier: MIT
'''


def IsInAliases(single_verbose_license):
    CSVfilePath = "../../csv/spdx-id.csv"
    IsInAliases = False
    with open(CSVfilePath, 'rt') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if single_verbose_license == row[0]:
                print(single_verbose_license+" is a recognized Alias")
                IsInAliases = True
                return IsInAliases
        if not IsInAliases:
            #print(single_verbose_license+" is a not recognized Alias")
            return IsInAliases


def IsAnSPDX(license_name):
    IsSPDX = False
    with open('../../csv/SPDX_license_name.csv', 'rt') as f:
        reader = csv.reader(f)
        for row in reader:
            for field in row:
                if field.lower() == license_name.lower():
                    IsSPDX = True
                    return IsSPDX


def ConformWithSPDX(license_name):
    with open('../../csv/SPDX_license_name.csv', 'rt') as f:
        reader = csv.reader(f)
        for row in reader:
            for field in row:
                if field.lower() == license_name.lower():
                    license_name = field
                    return license_name