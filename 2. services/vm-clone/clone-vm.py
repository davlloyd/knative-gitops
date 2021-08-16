from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect

import atexit, argparse, getpass, ssl, json
import os

from flask import Flask, request

app = Flask(__name__)

def wait_for_task(task):
    """ wait for a vCenter task to finish """
    task_done = False
    while not task_done:
        if task.info.state == 'success':
            return task.info.result

        if task.info.state == 'error':
            app.logger.error("Clone operation error")
            app.logger.error(task.info.error)
            task_done = True

def get_obj(content, vimtype, name):
    """
    Return an object by name, if name is None the
    first found object is returned
    """
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                break
        else:
            obj = c
            break
    return obj


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

def clone_vm(
        content, template, vm_name, si,
        datacenter_name, vm_folder, host_name,
        resource_pool, power_on, git_path):
    """
    Clone a VM from a template/VM, datacenter_name, vm_folder, datastore_name
    cluster_name, resource_pool, and power_on are all optional.
    """

    # if none git the first one
    datacenter = get_obj(content, [vim.Datacenter], datacenter_name)

    if vm_folder:
        destfolder = get_obj(content, [vim.Folder], vm_folder)
    else:
        destfolder = datacenter.vmFolder

    host = get_obj(content, [vim.HostSystem], host_name)
    resource_pool = get_obj(content, [vim.ResourcePool], resource_pool)

    app.logger.info("Create RelocateSpec")
    relospec = vim.vm.RelocateSpec()
    relospec.datastore = template.datastore[0]
    relospec.pool = resource_pool
    relospec.host = host

    app.logger.info("Create ConfigSpec")
    vmconf = vim.vm.ConfigSpec()
    annotation = "git:" + git_path
    vmconf.annotation = annotation

    app.logger.info("Create CloneSpec")
    clonespec = vim.vm.CloneSpec()
    clonespec.location = relospec
    clonespec.powerOn = power_on
    clonespec.config = vmconf

    app.logger.info("Commencing clone operation")
    task = template.Clone(folder=destfolder, name=vm_name, spec=clonespec)
    wait_for_task(task)
    app.logger.info("Clone operation complete")
    return clonespec, task.info.state

@app.route('/', methods=['POST'])
def construct():
    """
    Let this thing fly
    """
    app.logger.info("VM Clone task called")

    if eval_values():
        app.logger.info("Data Evaluated successfully:")

    data = request.get_json()

    host = data.get("host")
    port = data.get("port", 443)
    if host is None:
        raise Exception("Host required")
 
    username = os.getenv('VC_ACCOUNT')
    password = os.getenv('VC_PASSWORD')


    template_name = data.get("template")
    name = data.get("name")
    dc_name = data.get("datacenterName")
    host_name = data.get("hostName")
    vm_folder = data.get("vmFolder")
    resource_pool = data.get("resourcePool")
    power_on = data.get("powerOn", False)
    git_path = data.get("gitPath", "unset")

    # connect this thing
    context = None
    app.logger.info("Connecting to vCenter")
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
    si = SmartConnect(
        host=host,
        user=username,
        pwd=password,
        port=port,
        sslContext=context)
    try:
        comment = None
        content = si.RetrieveContent()
        app.logger.info("Retrieving template")
        template = get_obj(content, [vim.VirtualMachine], template_name)
        state = "unknown"
        clonespec = None
        if template:
            clonespec, state = clone_vm(
                content, template, name, si,
                dc_name, vm_folder,
                host_name, resource_pool,
                power_on, git_path)
        else:
            app.logger.info("Template not found")
            state = "error"
            comment = "template not found"
        return {
            "state": state, 
            "comment": comment, 
            "vm": name, 
            "template": template_name, 
            "dc": dc_name,
            "respool": resource_pool
        }

    finally:
        Disconnect(si)


if __name__ == "__main__":
   app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))

