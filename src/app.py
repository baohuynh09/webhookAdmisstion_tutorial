import base64
import copy
import http
import json
import random

import jsonpatch
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/validate", methods=["POST"])
def validate():
    allowed = True
    try:
        for container_spec in request.json["request"]["object"]["spec"]["containers"]:
            if "env" in container_spec:
                allowed = False
    except KeyError:
        pass
    return jsonify(
        {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {
                "allowed": allowed,
                "uid": request.json["request"]["uid"],
                "status": {"message": "env keys are prohibited"},
            }
        }
    )


@app.route("/mutate", methods=["POST"])
def mutate():
    spec = request.json["request"]["object"]
    modified_spec = copy.deepcopy(spec)

    stringBefore = request.json["request"]["object"]["spec"]["containers"][0]["image"]
    stringChange = stringBefore.replace("docker.io","haha")
    print("stringBefore: {0}".format(stringBefore))
    print("stringChange: {0}".format(stringChange))

    try:
        #modified_spec["metadata"]["labels"]["mutating"] = str(
        #    random.randint(9990, 9999)
        #)
        modified_spec["spec"]["containers"][0]["image"] = stringChange
    except KeyError:
        pass

    patch = jsonpatch.JsonPatch.from_diff(spec, modified_spec)
    print("patch: {0}".format(patch))
    return jsonify(
        {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {
                "allowed": True,
                "uid": request.json["request"]["uid"],
                "patch": base64.b64encode(str(patch).encode()).decode(),
                "patchType": "JSONPatch",
            }
        }
    )


@app.route("/health", methods=["GET"])
def health():
    return ("", http.HTTPStatus.NO_CONTENT)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)  # pragma: no cover
