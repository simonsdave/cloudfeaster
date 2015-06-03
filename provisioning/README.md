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

```bash
   2  fleetctl
    3  fleetctl list-machines
    4  curl http://127.0.0.1:49153
    5  curl http://127.0.0.1:49153/fleet/v1/units
    6  systemctl
    7  systemctl | grep fleet
    8  systemctl fleet.socket
    9  systemctl fleet.socket status
   10  systemctl status fleet.socket
   11  systemctl status fleet.service
   12  systemctl status fleet.service -l
   13  journalctl
   14  journalctl etcd.service
   15  systemctl etcd.service
   16  systemctl status etcd.service
   17  systemctl status etcd.service -l
   18  exit
   19  history
```

#References
http://blog.michaelhamrah.com/2015/03/deploying-docker-containers-on-coreos-with-the-fleet-api/
https://www.digitalocean.com/community/tutorials/how-to-use-confd-and-etcd-to-dynamically-reconfigure-services-in-coreos
