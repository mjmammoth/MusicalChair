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
        self.query_results = None

    def document(self, doc_id):
        if doc_id not in self.data:
            self.data[doc_id] = {}
        return DocumentReferenceMock(self.data[doc_id])

    def add(self, data):
        doc_id = str(len(self.data) + 1)
        self.data[doc_id] = data
        return DocumentReferenceMock(self.data[doc_id])

    def where(self, field, op, value):
        if op == '==':
            self.query_results = [doc for doc in self.data.values() if doc.get(field) == value]
        elif op == '<':
            self.query_results = [doc for doc in self.data.values() if doc.get(field) < value]
        elif op == '>':
            self.query_results = [doc for doc in self.data.values() if doc.get(field) > value]
        return self

    def order_by(self, field):
        if self.query_results is not None:
            self.query_results = sorted(self.query_results, key=lambda doc: doc.get(field))
        return self

    def limit(self, limit):
        if self.query_results is not None:
            self.query_results = self.query_results[:limit]
        return self

    def get(self):
        if self.query_results is not None:
            return QuerySnapshotMock(self.query_results, self)
        else:
            return QuerySnapshotMock(list(self.data.values()), self)


class DocumentReferenceMock:

    def __init__(self, data):
        self.data = data

    def get(self):
        return DocumentSnapshotMock(self.data)

    def set(self, data):
        self.data.update(data)


class QuerySnapshotMock:
    def __init__(self, data, collection_ref):
        self.data = data
        self.collection_ref = collection_ref

    def __iter__(self):
        return iter([DocumentSnapshotMock(doc) for doc in self.data])

    def __getitem__(self, index):
        return DocumentSnapshotMock(self.data[index])


class DocumentSnapshotMock:
    def __init__(self, data):
        self.data = data
        self.reference = DocumentReferenceMock(data)

    def to_dict(self):
        return self.data

    @property
    def exists(self):
        return bool(self.data)
