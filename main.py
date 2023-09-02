import json
import weekdb.utils as utils


class ExistenceError(Exception):
    ...


class Collection:
    def __init__(self, name: str, data: list, connection) -> None:
        """
        It is a container for storing and processing documents (dict).\n
        It implements CRUD (Create, Read, Update, Delete):\n
        \t1. get() - gets one document from the collection by the specified id in the form of a dict\n
        \t2. filter() - gets several documents by the specified fields in the form of a list in which documents are stored in the form of a dict
        \t3. exclude() - gets multiple documents that do not match the specified fields
        \t4. exists() - checks the existence of a document by id
        \t5. add() - adds a new document to the collection
        \t6. update() - replaces the old document with the specified new one, the _id fields must match in the new and old document
        \t7. delete() - removes a document from the collection by the specified id
        \t8. count() - counts the number of documents in the collection
        \t9. save() - inherited from Connection.save(), saves all data to the specified .json file
        """
        self.__name: str = utils.is_type(name, str)
        self.__data: list = utils.is_type(data, list)
        self.__connection = connection

    def __str__(self) -> str:
        return f"<Collection:{self.__name}"

    def __get_name(self, name: any) -> str:
        return f"<doc_id:{name}>"

    @property
    def name(self) -> str:
        return self.__name

    def all(self) -> list:
        return self.__data

    def get(self, id: any) -> dict:
        return self.__data[utils.binary_search_document(self.__data, id)]

    def last(self, count: int = None) -> dict | list:
        if count:
            result = []
            for i in range(1, count + 1):
                result.append(self.__data[-i])

            return result

        return self.__data[-1]

    def filter(self, params: dict) -> list:
        result = []

        for doc in self.all():

            test = 0

            for name, value in utils.is_type(params, dict).items():
                if name in doc:
                    if value == doc[name]:
                        test += 1

            if test == len(params):
                result.append(doc)

        return result

    def exclude(self, params: dict) -> list:
        result: list = []

        for doc in self.all():

            test = 0

            for name, value in utils.is_type(params, dict).items():
                if name in doc:
                    if value == doc[name]:
                        test += 1

            if test == 0:
                result.append(doc)

        return result

    def exists(self, id: any) -> bool:
        try:
            self.get(id)
            return True
        except utils.SearchError:
            return False

    def add(self, data: dict, again: bool = True) -> dict:
        data = utils.is_type(data, dict)
        if "_id" in data:
            if not self.exists(data.get("_id")):
                self.__data.append(data)
                return data
            raise ExistenceError(
                f"document with {self.__get_name(data.get('_id'))} already exists")
        else:
            data["_id"] = utils.generate_random_key()

            while self.exists(data.get("_id")):
                data["_id"] = utils.generate_random_key()

            self.__data.append(data)

    def update(self, data: dict) -> None:
        data = utils.is_type(data, dict)
        if "_id" in data:
            if self.exists(data.get("_id")):
                index = utils.binary_search_document(
                    self.__data, data.get("_id"))
                self.__data[index] = data
                return data
            raise ExistenceError(
                f"document with {self.__get_name(data.get('_id'))} does not exist")
        raise ExistenceError("_id field is required")

    def delete(self, id: any) -> None:
        if self.exists(id):
            index = utils.binary_search_document(self.__data, id)
            self.__data.pop(index)
            return
        raise ExistenceError(
            f"document with {self.__get_name(id)} does not exist")

    def count(self) -> int:
        return len(self.__data)

    def save(self) -> None:
        self.__connection.save()


class Connection:
    def __init__(self, path: str) -> None:
        self.__path = utils.Path(path).get()

        with open(self.__path, "r", encoding="utf-8") as file:
            try:
                data: dict = json.load(file)
            except json.decoder.JSONDecodeError:
                data: dict = {}

        self.__collections = [name for name in data]
        self.__data = {}

        for name, value in data.items():
            self.__data[name] = Collection(name, value, self)

    def __get_name(self, name: any) -> str:
        return f"<Collection:{name}"

    def __str__(self) -> str:
        return f"<Connection:{id(self)}"

    @property
    def collections(self):
        return self.__collections

    def get_collection(self, name: str) -> Collection:
        if utils.is_type(name, str) in self.__data:
            return self.__data.get(name)
        raise ExistenceError(
            f"collection {self.__get_name(name)} does not exist")

    def add_collection(self, name: str, again: bool = False) -> Collection:
        if not utils.is_type(name, str) in self.__data:
            self.__collections.append(name)
            self.__data[name] = Collection(name, [], self)
            return self.get_collection(name)
        if not again:
            raise ExistenceError(
                f"collection {self.__get_name(name)} already exists")
        return self.get_collection(name)

    def delete_collection(self, name: str) -> None:
        if utils.is_type(name, str) in self.__data:
            self.__collections.remove(name)
            self.__data.pop(name)
            return
        raise ExistenceError(
            f"collection {self.__get_name(name)} does not exist")

    def save(self):
        data = {}

        for name, value in self.__data.items():
            sorted_value = sorted(value.all(), key=lambda x: x["_id"])
            data[name] = sorted_value

        with open(self.__path, "w+", encoding="utf-8") as file:
            json.dump(data, file)
