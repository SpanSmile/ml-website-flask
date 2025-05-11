yaml_template = """
apiVersion: v1
kind: Pod
metadata:
  name: {{ job_name }}
  labels:
    runai/queue: test
  annotations:
    gpu-memory: "{{ gpu_memory }}"
spec:
  schedulerName: kai-scheduler
  containers:
    - name: trainer
      image: {{ image }}
      volumeMounts:
        - name: nfs-storage
          mountPath: /mnt/nfs/training-results
  restartPolicy: Never
  volumes:
    - name: nfs-storage
      nfs:
        server: {{ nfs_server }}
        path: {{ nfs_path }}
        readOnly: false
"""
