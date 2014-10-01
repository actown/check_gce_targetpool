#!/usr/bin/env python
import json
import pynagios
import requests
from pynagios import Plugin
from pynagios import make_option
from pynagios import Response


class CheckGceTargetpool(Plugin):
    gce_project_id = make_option("--project-id", type="string")
    gce_targetpool = make_option("--targetpool", type="string")
    gce_targetpool_instance = make_option("--targetpool-instance",
                                          type="string")
    gce_region = make_option("--region", type="string")
    gce_zone = make_option("--zone", type="string")

    def check(self):
        try:
            auth_code = requests.get('http://metadata/computeMetadata/v1/instance/service-accounts/default/token', headers={'Metadata-Flavor': 'Google'})
            if auth_code.status_code is not 200:
                return Response(pynagios.UNKNOWN,
                                ("The Google token url status code is"
                                 "not 200."))
            token = auth_code.json()['access_token']
        except:
            return Response(pynagios.UNKNOWN,
                            ("Unable to get the auth token from Google."))

        instance_json = {'instance': 'https://www.googleapis.com/compute/v1/projects/' + self.options.gce_project_id + '/zones/' + self.options.gce_region + '-' + self.options.gce_zone + '/instances/' + self.options.gce_targetpool_instance}
        try:
            health_state = requests.post('https://www.googleapis.com/compute/v1/projects/' + self.options.gce_project + '/regions/' + self.options.gce_region + '/targetPools/' + self.options.gce_targetpool + '/getHealth', data=json.dumps(instance_json), headers={'Authorization': 'Bearer ' + token})
            if health_state.status_code is not 200:
                return Response(pynagios.UNKNOWN,
                                ("The Google getHealth url status code is"
                                 "not 200."))
            health_status = health_state.json()['healthStatus']['healthState']
        except:
            return Response(pynagios.UNKNOWN,
                            ("Unable to get the health status from Google."))

        if health_status is 'HEALTHY':
            return Response(pynagios.OK,
                            ("The targetpool is healthy."))
        else:
            return Response(pynagios.CRITICAL,
                            ("The targetpool is unhealthy."))


if __name__ == "__main__":
    CheckGceTargetpool().check().exit()

