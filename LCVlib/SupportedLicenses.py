import pandas as pd
import numpy as np
import csv
from LCVlib.VerboseLicenseParsing import DetectWithAcronyms, DetectWithKeywords, ConformVersionNumber, RemoveParenthesisAndSpecialChars

'''
* SPDX-FileCopyrightText: 2023 Michele Scarlato <michele.scarlato@gmail.com>
*
* SPDX-License-Identifier: MIT
'''


def supported_licenses_(CSVfilePath):
    df = pd.read_csv(CSVfilePath, usecols=column_names_list)
    supported_licenses_OSADL = list(df.index)
    print('Licenses supported by the compatibility matrix:')
    for a, b, c, d, e in zip(supported_licenses_OSADL[::5], supported_licenses_OSADL[1::5], supported_licenses_OSADL[2::5],
                             supported_licenses_OSADL[3::5], supported_licenses_OSADL[4::5]):
        print('{:<30}{:<30}{:<}'.format(a, b, c, d, e))
