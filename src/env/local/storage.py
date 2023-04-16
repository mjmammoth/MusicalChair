import json

from google.cloud import firestore


class FirestoreClientMock:
    def __init__(self, file_path='firestore_data.json'):
        self.file_path = file_path
        self.data = self._load_data_from_file()

    def _load_data_from_file(self):
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        return data

    def _write_data_to_file(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file)

    def collection(self, name):
        if name not in self.data:
            self.data[name] = {}
            self._write_data_to_file()
        return CollectionReferenceMock(self.data[name], self)


class CollectionReferenceMock:
    def __init__(self, data, firestore_client):
        self.data = data
        self.firestore_client = firestore_client

    def document(self, doc_id):
        if doc_id not in self.data:
            self.data[doc_id] = {}
            self.firestore_client._write_data_to_file()
        return DocumentReferenceMock(self.data[doc_id], self.firestore_client)

    def add(self, data):
        doc_id = str(len(self.data) + 1)
        self.data[doc_id] = data
        self.firestore_client._write_data_to_file()
        return DocumentReferenceMock(self.data[doc_id], self.firestore_client)

    def where(self, field, op, value):
        return QueryReferenceMock(self).where(field, op, value)

    def order_by(self, field):
        if self.query_results is not None:
            self.query_results = sorted(
                self.query_results, key=lambda doc: doc.get(field))
        return self

    def limit(self, limit):
        if self.query_results is not None:
            self.query_results = self.query_results[:limit]
        return self

    def get(self):
        if not self.data:
            return QuerySnapshotMock([], self.firestore_client)
        else:
            return QuerySnapshotMock(list(self.data.values()), self.firestore_client)

    def stream(self):
        if not self.data:
            return iter([])
        else:
            return iter([DocumentSnapshotMock(doc, self.firestore_client) for doc in self.data.values()])

    def __str__(self):
        return f'CollectionReferenceMock({self.data})'


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
                query_results = [
                    doc for doc in query_results if doc.get(field) == value]
            elif op == '<':
                query_results = [
                    doc for doc in query_results if doc.get(field) < value]
            elif op == '>':
                query_results = [
                    doc for doc in query_results if doc.get(field) > value]
            else:
                raise ValueError(f'Invalid operator: {op}')
        return QuerySnapshotMock(query_results, self.collection_ref.firestore_client)

    def order_by(self, field):
        # ...
        return self

    def limit(self, limit):
        # ...
        return self


class DocumentReferenceMock:
    def __init__(self, data, firestore_client):
        self.data = data
        self.firestore_client = firestore_client

    def get(self):
        return DocumentSnapshotMock(self.data, self.firestore_client)

    def set(self, data):
        self.data.update(data)
        self.firestore_client._write_data_to_file()

    def update(self, data):
        for key, value in data.items():
            if isinstance(value, firestore.ArrayUnion):
                if key not in self.data:
                    self.data[key] = []
                self.data[key].extend(value.values)
            else:
                self.data[key] = value
        self.firestore_client._write_data_to_file()

    @property
    def exists(self):
        return bool(self.data)


class QuerySnapshotMock:
    def __init__(self, data, firestore_client):
        self.data = data
        self.firestore_client = firestore_client

    def __iter__(self):
        return iter([DocumentSnapshotMock(doc, self.firestore_client) for doc in self.data])

    def __getitem__(self, index):
        return DocumentSnapshotMock(self.data[index], self.firestore_client)

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return str(self.data)


class DocumentSnapshotMock:
    def __init__(self, data, firestore_client):
        self.data = data
        self.firestore_client = firestore_client

    @property
    def reference(self):
        return DocumentReferenceMock(self.data, self.firestore_client)

    def to_dict(self):
        return self.data

    @property
    def exists(self):
        return bool(self.data)
