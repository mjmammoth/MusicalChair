from google.cloud import firestore


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

    def where(self, field, op, value):
        return QueryReferenceMock(self).where(field, op, value)

    def order_by(self, field):
        if self.query_results is not None:
            self.query_results = sorted(self.query_results, key=lambda doc: doc.get(field))
        return self

    def limit(self, limit):
        if self.query_results is not None:
            self.query_results = self.query_results[:limit]
        return self

    def get(self):
        if not self.data:
            return QuerySnapshotMock([])
        else:
            return QuerySnapshotMock(list(self.data.values()))

    def stream(self):
        if not self.data:
            return iter([])
        else:
            return iter([DocumentSnapshotMock(doc) for doc in self.data.values()])


class QueryReferenceMock:
    def __init__(self, collection_ref):
        self.collection_ref = collection_ref
        self.conditions = []

    def where(self, field, op, value):
        self.conditions.append((field, op, value))
        return self

    def get(self):
        query_results = self.collection_ref.data.values()
        for field, op, value in self.conditions:
            if op == '==':
                query_results = [doc for doc in query_results if doc.get(field) == value]
            elif op == '<':
                query_results = [doc for doc in query_results if doc.get(field) < value]
            elif op == '>':
                query_results = [doc for doc in query_results if doc.get(field) > value]
            else:
                raise ValueError(f'Invalid operator: {op}')
        return QuerySnapshotMock(query_results)

    def order_by(self, field):
        # ...
        return self

    def limit(self, limit):
        # ...
        return self


class DocumentReferenceMock:
    def __init__(self, data):
        self.data = data

    def get(self):
        return DocumentSnapshotMock(self.data)

    def set(self, data):
        self.data.update(data)

    def update(self, data):
        for key, value in data.items():
            if isinstance(value, firestore.ArrayUnion):
                if key not in self.data:
                    self.data[key] = []
                self.data[key].extend(value.values)
            else:
                self.data[key] = value

    @property
    def exists(self):
        return bool(self.data)



class QuerySnapshotMock:
    def __init__(self, data):
        self.data = data

    def __iter__(self):
        return iter([DocumentSnapshotMock(doc) for doc in self.data])

    def __getitem__(self, index):
        return DocumentSnapshotMock(self.data[index])

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return str(self.data)


class DocumentSnapshotMock:
    def __init__(self, data):
        self.data = data
        self.reference = DocumentReferenceMock(data)

    def to_dict(self):
        return self.data

    @property
    def exists(self):
        return bool(self.data)
