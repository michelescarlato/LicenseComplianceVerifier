from LCVlib.verify import retrieveOutboundLicense, CompareSPDX, CompareSPDXFlag, CompareSPDX_OSADL, Compare_OSADL, \
    Compare_OSADLFlag
from LCVlib.SPDXIdMapping import ConvertToSPDX, IsAnSPDX
from dotenv import load_dotenv
from os import environ, path
import os
from flask import request, jsonify, render_template
import re
import flask
import argparse

'''
* SPDX-FileCopyrightText: 2023 Michele Scarlato <michele.scarlato@gmail.com>
*
* SPDX-License-Identifier: MIT
'''

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
PATH = environ.get('PATH')
LOGFILE = environ.get('LOGFILE')
PORT = environ.get('PORT')
HOST = environ.get('HOST')
GITREPO = environ.get('GITREPO')


# Check the port number range
class PortAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not 0 < values < 2 ** 16:
            raise argparse.ArgumentError(
                self, "port numbers must be between 0 and 65535")
        setattr(namespace, self.dest, values)


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port",
                    help='Port number to connect to',
                    dest=PORT,
                    default=3251,
                    type=int,
                    action=PortAction,
                    metavar="{0..65535}")
parser.add_argument("-P", "--PATH",
                    help='PATH environment override',
                    dest='PATH',
                    # default=environ.get('PYTHONHOME'),
                    type=str)
args = parser.parse_args()
if args.port:
    PORT = args.port
if args.PATH:
    PATH = args.PATH

os.environ['PATH'] = PATH

app = flask.Flask(__name__)
app.config["DEBUG"] = True


# logging.basicConfig(filename=LOGFILE, level=logging.DEBUG)


@app.route('/APIEndpoints')
def api_endpoints():
    return render_template('APIEndpoints.html')


@app.route('/CompatibilitySPDX')
def compatibility_spdx():  # this endpoint is a html interface where list of
    # licenses can be checked against the outbound license
    return render_template('compatibilitySPDX.html')


@app.route('/CompatibilitySPDXOutput', methods=['POST', 'GET'])
def compliance_spdx():  # this endpoint is coupled with the compatibility_spdx endpoint,
    # and provides the verification's output.
    if request.method == 'POST':
        InboundLicenses = request.form['inboundLicenses']
        InboundLicenses = InboundLicenses.split(",")
        OutboundLicense = request.form['outboundLicense']
        verificationList = CompareSPDX(InboundLicenses, OutboundLicense)
        return jsonify(verificationList)


@app.route('/CompatibilitySPDXFlag')
def CompatibilitySPDXFlag():
    return render_template('compatibilitySPDXFlag.html')


@app.route('/CompatibilitySPDXFlagOutput', methods=['POST', 'GET'])
def ComplianceSPDXFlag():
    if request.method == 'POST':
        InboundLicenses = request.form['inboundLicenses']
        InboundLicenses = InboundLicenses.split(",")
        OutboundLicense = request.form['outboundLicense']
        verificationFlag = CompareSPDXFlag(InboundLicenses, OutboundLicense)
        # print(verificationList)
        return jsonify(verificationFlag)


@app.route('/GetGitHubOutboundLicense', methods=['POST', 'GET'])
def GetGitHubOutboundLicense():
    args = request.args
    url = args['url']
    OutboundLicense = retrieveOutboundLicense(url)
    return OutboundLicense


@app.route('/LicensesInputSPDX', methods=['GET', 'POST'])
# @app.route('/LicensesInput', methods=['POST'])
def LicensesInputSPDX():
    args = request.args
    # print(args)  # For debugging
    InboundLicenses = args['InboundLicenses']
    InboundLicenses = InboundLicenses.split(",")
    OutboundLicense = args['OutboundLicense']
    verificationList = CompareSPDX(InboundLicenses, OutboundLicense)
    return jsonify(verificationList)


@app.route('/LicensesInputSPDX_OSADL', methods=['POST', 'GET'])
def LicensesInputSPDX_OSADL():
    args = request.args
    print(args)  # For debugging
    InboundLicenses = args['InboundLicenses']
    InboundLicenses = InboundLicenses.split(",")
    OutboundLicense = args['OutboundLicense']
    verificationList = CompareSPDX_OSADL(InboundLicenses, OutboundLicense)
    return jsonify(verificationList)


# this endpoint perform the check upon the OSADL.csv
@app.route('/LicensesInput', methods=['POST', 'GET'])
def LicensesInput():
    args = request.args
    print(args)  # For debugging
    InboundLicenses = args['InboundLicenses']
    # InboundLicenses = InboundLicenses.split(";")
    InboundLicenses = re.split(';|OR', InboundLicenses)
    OutboundLicense = args['OutboundLicense']
    verificationList = Compare_OSADL(InboundLicenses, OutboundLicense)
    return jsonify(verificationList)


@app.route('/LicensesInputFlag', methods=['POST', 'GET'])
def licenses_input_flag():
    args = request.args
    print(args)  # For debugging
    InboundLicenses = args['InboundLicenses']
    InboundLicenses = InboundLicenses.split(";")
    OutboundLicense = args['OutboundLicense']
    verificationList = Compare_OSADLFlag(InboundLicenses, OutboundLicense)
    return jsonify(verificationList)


@app.route('/ConvertToSPDX', methods=['POST', 'GET'])
def ConvertToSPDXEndpoint():
    args = request.args
    print(args)  # For debugging
    VerboseLicense = args['VerboseLicense']
    SPDXid = ConvertToSPDX(VerboseLicense)
    return jsonify(SPDXid)


@app.route('/IsAnSPDX', methods=['POST', 'GET'])
def IsAnSPDXEndpoint():
    args = request.args
    print(args)  # For debugging
    SPDXid = args['SPDXid']
    Bool = IsAnSPDX(SPDXid)
    if Bool is None:
        Bool = False
    return jsonify(Bool)


@app.route('/LicensesInputSPDXFlag', methods=['GET', 'POST'])
# @app.route('/LicensesInput', methods=['POST'])
def LicensesInputSPDXFlag():
    args = request.args
    InboundLicenses = args['InboundLicenses']
    InboundLicenses = InboundLicenses.split(",")
    OutboundLicense = args['OutboundLicense']
    verificationFlag = CompareSPDXFlag(InboundLicenses, OutboundLicense)
    return jsonify(verificationFlag)


@app.route('/PATH', methods=['GET'])
def path():
    CurrentPath = os.getenv("PATH")
    return str(CurrentPath)




app.run(host=HOST, port=PORT)
