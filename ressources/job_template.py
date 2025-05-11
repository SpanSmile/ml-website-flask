yaml_template1 = """
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ job_name }}
  labels:
    runai/queue: test
  annotations:
    gpu-memory: "{{ gpu_memory }}"
spec:
  template:
    spec:
      schedulerName: kai-scheduler
      containers:
        - name: trainer
          image: {{ image }}
          command: ["/bin/bash", "-c"]
          args:
            - |
              cp -r /app/* /mnt/nfs && \
              python /mnt/nfs/train.py
          volumeMounts:
            - name: nfs-storage
              mountPath: /mnt/nfs
      restartPolicy: Never
      volumes:
        - name: nfs-storage
          nfs:
            server: {{ nfs_server }}
            path: {{ nfs_path }}
            readOnly: false
"""
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
