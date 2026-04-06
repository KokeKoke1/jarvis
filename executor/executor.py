import subprocess
import requests

def execute_task(task):
    ttype = task.get("type","shell")
    result = ""
    status = "done"
    try:
        if ttype == "shell":
            cmd = task["cmd"]
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
            result = output.strip()
        elif ttype == "api":
            url = task["url"]
            method = task.get("method","GET").upper()
            data = task.get("data")
            res = requests.request(method, url, json=data)
            result = res.text
        elif ttype == "file":
            path = task["path"]
            with open(path, "r") as f:
                result = f.read()
        else:
            result = "Nieznany typ tasku"
    except Exception as e:
        result = str(e)
        status = "error"
    task["result"] = result
    task["status"] = status
    return task