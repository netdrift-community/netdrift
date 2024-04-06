# netdrift
netdrift is a simple API designed to plug into orchestrators without abstracting the transport role of the orchestrator. Most orchestrators/systems will handle both SSH/HTTP/gRPC/TLS transport and configuration intent whether it be directly from the orchestrator or passed down to a worker that implements the transport mechansims, however netdrift's purpose is only to be used as a datastore to define the intent of the configuration, and provide useful endpoints to return config diffs along with webhook functionality to inform users of a config drift in the network.

The great thing here is that netdrift is not tied into a orchestrator setup so people can start to utilize the functionality straight away with a few simple API calls from their own internal systems or a script.

## Basic architecture



`to be updated`


## Notes

Intent discovery will use get-config to get full configuration, hash is made for this config to compare future intent jobs to see if any configuration has changed, this is a Full intent job, people can opt to use webhooks/notifications to be told when the full intent is out of sync with the device, however netdrift will never attempt to replace the full configuration.

Partial intent is intended for a user to track multiple parts of the configuration intent, for example:

- You can track each BGP neighbors intent separately, so that when you replace the intent for 1 neighbor, you are not performing a NETCONF replace operation on all your BGP neighbors
- You can track each Layer 2 VPN instance and configuration related to specific instances so you can again, perform a replace operation only on the relevant configuration that is out of sync, instead of trying to replace all of your layer 2 VPN instances.