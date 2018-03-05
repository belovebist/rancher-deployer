# rancher-deployer
A deployment cli for rancher. Designed to be used for CICD.

Rancher is very useful container management platform on top of kubernetes.
Also it provides very useful API that could be used to integrate it with our CICD pipeline.
"rancher-deployer" is a cli application written in python to be used to deploy application containers into cluster managed by rancher.

Currently service deployment (create, update, upgrade, delete) and loadbalancer (update rules) are implemented, but the API is written so that it can be extended easily to cover all the resource provided by rancher.

Hope this helps someone to get started with integrating rancher with CICD pipeline.
