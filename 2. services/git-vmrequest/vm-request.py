import requests
import json
import os

from flask import Flask, request

app = Flask(__name__)

def eval_values():
    app.logger.info("Environment Variables:")
    for k, v in sorted(os.environ.items()):
        try:
            val = str(v)
        except:
            val = "unknown"
        logval = k + ':' + val
        app.logger.info(logval)

    app.logger.info("Request JSON payload:")
    data = request.get_json()
    app.logger.info(data)
    return True

def buildrequest(entry, fileurl):
    app.logger.info("Building request entry")
    host = "vcenter.home.local"
    template = "ubuntu-20-template"

    name = entry["name"]
    if "template" in entry:
        sourcetemplate = entry["template"]
    else:
        sourcetemplate = template
    if "targethost" in entry:
        targethost = entry["targethost"]
    else:
        targethost = host
    if "dc" in entry:
        targetdc = entry["dc"]
    if "vmfolder" in entry:
        targetfolder = entry["vmfolder"]
    if "resourcepool" in entry:
        respool = entry["resourcepool"]
    if "poweron" in entry:
        poweron = entry["poweron"]
    else:
        poweron = False

    clone_data = {
        'host': targethost, 
        'name': name, 
        'template': sourcetemplate,
        'datacenterName': targetdc,
        'vmFolder': targetfolder,
        'resourcePool': respool,
        'powerOn': poweron,
        'gitPath': fileurl
        }
    
    app.logger.info(clone_data)

    return clone_data


@app.route('/', methods=['POST'])
def main():
    app.logger.info("Git Push event being processed")
    eval_values()

    # URL populated by associated Sink binding with vmclone service
    clone_url = os.environ["K_SINK"]
    app.logger.info(clone_url)
    
    data = json.loads(request.data)
    repopath = data["repository"]["homepage"]
    filerequests = data["commits"][0]["added"]

    vmlist = ""
    if (len(filerequests)):
        for filename in filerequests:
            if "template" not in filename.lower():
                file_url = '{0}/-/raw/main/{1}'.format(repopath, filename)
                app.logger.info("Reading request file")
                app.logger.info(file_url)
                response = requests.get(file_url)
                if response.status_code == 200:
                    entry = response.json()
                    clone_data=buildrequest(entry, file_url)

                    response = requests.post(
                        clone_url, 
                        data=json.dumps(clone_data),
                        headers={'Content-Type': 'application/json'},
                        verify=False
                    )
                    vmlist += "{0}/n".format(clone_data)
                else:
                    print(file_url)
    else:
        return {"status": "no new requests", "message": "Nothing to do"}

    return {"status": "done", "message": vmlist}

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))

