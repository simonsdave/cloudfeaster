* generate a token for the new cluster
```bash
>curl -w "\n" 'https://discovery.etcd.io/new?size=3'
https://discovery.etcd.io/c421d572510cbc5099de50c8f352285c
>
```

* per [these](https://coreos.com/docs/running-coreos/cloud-providers/google-compute-engine/)
create a ```cloud-config.yaml``` file

* spin up a 3 node cluster
```bash
gcloud compute instances create core1 core2 core3 --image https://www.googleapis.com/compute/v1/projects/coreos-cloud/global/images/coreos-stable-647-2-0-v20150528 --zone us-central1-a --machine-type n1-standard-1 --metadata-from-file user-data=cloud-config.yaml
```
