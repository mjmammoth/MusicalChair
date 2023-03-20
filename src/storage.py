class LocalCollection:

    def __init__(self):
        self.store = dict()

    def to_dict(self):
        """Mimics GCP Firestore method."""
        return self.store

    @property
    def exists(self):
        """Mimics GCP Firestore method."""
        return bool(self.store)
    

class LocalFirestore:

    def __init__(self):
        self.collection = LocalCollection()

    def get(self):
        return self.collection

    def set(self, data):
        self.collection.store = data


class LocalBlob:

    def __init__(self):
        self.data = None

    def upload_from_string(self, data):
        self.data = data

    def download_as_string(self):
        return self.data


class LocalBucket:

    def __init__(self):
        self.blobs = dict()

    def get_blob(self, name):
        return self.blobs.get(name, None)

    def blob(self, name):
        self.blobs[name] = LocalBlob()
        return self.blobs[name]
