class FirestoreClientMock:
    def __init__(self):
        self.data = {}

    def collection(self, name):
        if name not in self.data:
            self.data[name] = {}
        return CollectionReferenceMock(self.data[name])


class CollectionReferenceMock:

    def __init__(self, data):
        self.data = data

    def document(self, doc_id):
        if doc_id not in self.data:
            self.data[doc_id] = {}
        return DocumentReferenceMock(self.data[doc_id])

    def add(self, data):
        doc_id = str(len(self.data) + 1)
        self.data[doc_id] = data
        return DocumentReferenceMock(self.data[doc_id])


class DocumentReferenceMock:

    def __init__(self, data):
        self.data = data

    def get(self):
        return DocumentSnapshotMock(self.data)

    def set(self, data):
        self.data.update(data)


class DocumentSnapshotMock:
    def __init__(self, data):
        self.data = data

    def to_dict(self):
        return self.data

    @property
    def exists(self):
        return bool(self.data)
