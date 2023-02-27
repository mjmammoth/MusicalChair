Intended to be deployed in Cloud Run and triggered by Cloud Scheduler (cronjob)
Uses firestore for persistence:
- collection: `exclusions`
- document: `state`
