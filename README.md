# Thesis
This project includes some minor modifications to enable job submission to Kubernetes.

You can find the original repository [HERE](https://github.com/firas-ben-thayer/ml-website-flask).

In this test we didnt add the code server

## Changes Made
- Added a page for submitting jobs in a form
- Added functionality to access `kubectl` by providing the cluster's kubeconfig
- Added a YAML template for defining a pod
- Added a new route to support this setup

## Limitation
- The code server was not added as part of this implementation but can be found in the original repository.
