#!/usr/bin/env python3

import os
import json
import requests
import datetime
import subprocess
from flask import Flask, Response

def get_nic():
    for k in os.listdir('/sys/class/net'):
        if k != 'lo':
            return k;
# Base dir of the html, css and js files
BASEDIR='/var/www'
# MEC Service endpoint
MEC_SERVICE_MGMT="mec_service_mgmt/v1"
# MEC Application endpoint
MEC_APP_SUPPORT="mec_app_support/v1"
# Callback proposed
CALLBACK_URL='/_mecSerMgmtApi/callback'

# Get interfaces
INTERFACE=get_nic()

# XXX Unsupported in alpine atm.
PTP_COMMAND="ptp4l -A -4 -S -i {}".format(INTERFACE)

OTHER_APPLICATION_URI='/icommMMTCSlicingService'

app = Flask(__name__)

# MEC Base Endpoint
mec_base = ''

service_id = ''
app_instance_id = ''
transportlist = [ { 'id': 'TransId12345' } ]

application_notified = False

other_application_endpoint = ''

# Transport API
@app.route('/transports')
def transports():
    global mec_base
    query_base = "{}/{}/transports".format(
            mec_base,
            MEC_SERVICE_MGMT
    )
    r = requests.get(query_base)

    return r.text

# Services API
@app.route('/services')
def services():
    global mec_base
    global app_instance_id
    out = ''
    query_base = "{}/{}/applications/{}/services".format(
            mec_base,
            MEC_SERVICE_MGMT,
            app_instance_id
    )

    r = requests.get(query_base)

    return r.text

# Subscribe to service
@app.route('/services/subscribe')
def service_subscribe():
    global mec_base
    global service_id
    global transportlist
    global app_instance_id

    data = {
      "serName": "UniboMECService",
      "serCategory": {
        "href": "/example/catalogue1",
        "id": "id12345",
        "name": "RNI",
        "version": "v1"
      },
      "version": "ServiceVersion1",
      "state": "ACTIVE",
      "transportId": "Rest1",
      "transportInfo": {
        "id": '{}'.format(transportlist[0]['id']),
        "name": "REST",
        "description": "REST API",
        "type": "REST_HTTP",
        "protocol": "HTTP",
        "version": "2.0",
        "endpoint": {
        },
      "security": {
        "oAuth2Info": {
          "grantTypes": [
            ""
          ],
          "tokenEndpoint": ""
        }
      },
      "implSpecificInfo": {}
      },
      "serializer": "JSON",
      "scopeOfLocality": "MEC_SYSTEM",
      "consumedLocalOnly": True,
      "isLocal": True
    }

    query_base = "{}/{}/applications/{}/services".format(
            mec_base,
            MEC_SERVICE_MGMT,
            app_instance_id
    )

    headers = {"content-type": "application/json"}
    r = requests.post(query_base, data=json.dumps(data), headers=headers)

    # XXX we don't have any slash in the url?
    service_id = r.headers['location'].split('/')[-1]

    return 'New service_id: {}'.format(service_id)

# Unsubscribe a service
@app.route('/services/unsubscribe')
def service_unsubscribe():
    global mec_base
    global service_id
    global app_instance_id
    query_base = "{}/{}/applications/{}/services/{}".format(
            mec_base,
            MEC_SERVICE_MGMT,
            app_instance_id,
            service_id
    )
    r = requests.delete(query_base)
    return r.text

# Get DNS Rules
@app.route('/dns_rules')
def dns_rules():
    global mec_base
    global dns_rules
    global app_instance_id

    query_base = "{}/{}/applications/{}/dns_rules".format(
            mec_base,
            MEC_APP_SUPPORT,
            app_instance_id
    )
    r = requests.get(query_base)

    dns_rules = json.loads(r.text)

    return r.text

# Modify DNS rules
@app.route('/dns_rules/<modification>')
def dns_rule_modify(modification):
    global mec_base
    global dns_rules
    global app_instance_id
    dns_rule = dns_rules[0]

    query_base = "{}/{}/applications/{}/dns_rules/{}".format(
            mec_base,
            MEC_APP_SUPPORT,
            app_instance_id,
            dns_rule['dnsRuleId']
    )

    dns_rule["state"] = modification
    headers = { 'content-type': 'application/json' }
    r = requests.put(query_base, data=json.dumps(dns_rule), headers=headers)
    return json.dumps(dns_rule)

# Notifications API
@app.route('/notifications')
def notifications():
    global mec_base
    global app_instance_id
    query_base = "{}/{}/applications/{}/subscriptions".format(
            mec_base,
            MEC_SERVICE_MGMT,
            app_instance_id
    )

    r = requests.get(query_base)

    return r.text

# Subscribe to notifications
@app.route('/notifications/subscribe')
def notifications_subscribe():
    global mec_base
    global service_id
    global app_instance_id

    # Catch all notification endpoint
    data = {
      "subscriptionType": "SerAvailabilityNotificationSubscription",
      "callbackReference": "string",
      "_links": {
        "self": {
          "href": CALLBACK_URL
        }
      }
    }

    query_base = "{}/{}/applications/{}/subscriptions".format(
            mec_base,
            MEC_SERVICE_MGMT,
            app_instance_id
    )

    headers = {"content-type": "application/json"}
    r = requests.post(query_base, data=json.dumps(data), headers=headers)

    # XXX we don't have any slash in the url?
    service_id = r.headers['location'].split('/')[-1]

    return 'New notification_id: {}'.format(service_id)

# Unsubscribe notifications
@app.route('/notifications/unsubscribe')
def notification_unsubscribe():
    global mec_base
    global service_id
    global app_instance_id
    query_base = "{}/{}/applications/{}/subscriptions/{}".format(
            mec_base,
            MEC_SERVICE_MGMT,
            app_instance_id,
            service_id
    )
    r = requests.delete(query_base)
    return r.text

@app.route('/notifications/notify_ready')
def notification_confirm_ready():
    query_base = "{}/{}/applications/{}/confirm_ready".format(
            mec_base,
            MEC_APP_SUPPORT,
            app_instance_id
    )

    ready_indication = { "indication": "READY" }
    headers = { 'content-type': 'application/json' }

    r = requests.put(query_base, data=json.dumps(ready_indication), headers=headers)
    return r.text

# Time API
@app.route('/timings/timing_caps')
def timing_timing_caps():
    query_base = "{}/{}/timing/timing_caps".format(
            mec_base,
            MEC_APP_SUPPORT,
            app_instance_id,
            service_id
    )
    r = requests.get(query_base)
    return r.text

@app.route('/timings/current_time')
def timing_current_time():
    query_base = "{}/{}/timing/current_time".format(
            mec_base,
            MEC_APP_SUPPORT,
            app_instance_id,
            service_id
    )
    r = requests.get(query_base)
    return r.text

@app.route('/timings/_ptp_status')
def timing_ptp_status():
    global ptp_process
    if ptp_process.poll != None:
        return "Not Running"
    return "Running"

@app.route('/timings/_start_ptp')
def timing_ptp_start():
    global ptp_process
    if timing_ptp_status() != "Not Running":
        return "Already running"

    ptp_process = subprocess.Popen(PTP_COMMAND.split(" "))
    return "Unimplemented"

@app.route('/timings/_ptp_time')
def timing_ptp_time():
    return str(datetime.datetime.now())

# Get Traffic Rules
@app.route('/traffic_rules')
def traffic_rules():
    global mec_base
    global traffic_rules
    global app_instance_id

    query_base = "{}/{}/applications/{}/traffic_rules".format(
            mec_base,
            MEC_APP_SUPPORT,
            app_instance_id
    )
    r = requests.get(query_base)

    traffic_rules = json.loads(r.text)

    return r.text

# Modify DNS rules
@app.route('/traffic_rules/<modification>')
def traffic_rule_modify(modification):
    global mec_base
    global traffic_rules
    global app_instance_id
    traffic_rule = traffic_rules[0]

    query_base = "{}/{}/applications/{}/traffic_rules/{}".format(
            mec_base,
            MEC_APP_SUPPORT,
            app_instance_id,
            traffic_rule['trafficRuleId']
    )

    traffic_rule["state"] = modification
    headers = { 'content-type': 'application/json' }
    r = requests.put(query_base, data=json.dumps(traffic_rule), headers=headers)
    return json.dumps(traffic_rule)

# Catch all, return the retrieved file
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def catch_all(path):
    if '.ico' in path:
        return '';

    t = 'text/html'
    with open("{}/{}".format(BASEDIR,path)) as f:
        body = f.read()

    if '.css' in path:
        t = 'text/css'
    if '.js' in path:
        t = 'text/javascript'

    return Response(body, mimetype=t)

@app.route("/_get_application_notice")
def get_application_notice():
    global application_notified
    return str(application_notified);


# Callback for the notification framework
@app.route(CALLBACK_URL)
def service_notification_callback():
    global application_notified
    application_notified = True

    # XXX We should notify back using a structured json?
    return "ok"

# Query the other application
@app.route('/_contactapplication')
def contact_application():
    global other_application_endpoint
    query_base = "{}{}".format(
            other_application_endpoint,
            OTHER_APPLICATION_URI
    )

    r = requests.get(query_base)
    return r.text

if __name__=='__main__':
    app_instance_id = os.environ['APP_INSTANCE_ID']
    mec_base = os.environ['MEC_BASE']
    other_application_endpoint = os.environ['OTHER_APPLICATION_ENDPOINT']
    app.run("0.0.0.0", port=80)
