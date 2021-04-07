import pymongo


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class MongoSingleton(metaclass=SingletonMeta):
    def __init__(self, url: str, username: str, password: str, database: str) -> None:
        self.url = url
        self.username = username
        self.password = password
        self.database = database
        self.__connect_mongo()

    def __connect_mongo(self) -> None:
        self.client = pymongo.MongoClient(
            self.url, username=self.username, password=self.password
        )

    def set_url(self, url: str) -> None:
        self.url = url
        self.__connect_mongo()

    def set_username_and_password(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.__connect_mongo()

    def set_database(self, database: str) -> None:
        self.database = database

    def insert_new_dict(self, collection: str, new_dict: dict):
        mydb = self.client[self.database]
        mycol = mydb[collection]
        x = mycol.insert_one(new_dict)
        print(x.inserted_id)
        return x

    def update_dict(
        self, collection: str, id_key: str, id_value: str, new_dict: dict
    ):
        mydb = self.client[self.database]
        mycol = mydb[collection]
        mycol.update({id_key: id_value}, new_dict)

    def get_col(self, collection: str):
        return self.client[self.database][collection]

    def remove_collection(self, collection):
        mydb = self.client[self.database]
        mycol = mydb[collection]
        mycol.remove()


def load_mongo(cfg_mongo: dict) -> MongoSingleton:
    """Load a mongo class object"""
    try:
        ms = MongoSingleton(
            cfg_mongo["url"],
            cfg_mongo["username"],
            cfg_mongo["password"],
            cfg_mongo["database"],
        )
    except KeyError:
        list_keys = ["url", "username", "password", "database"]
        raise KeyError(
            f"Keys missing in cfg_mongo dictionary: "
            f"{(set(list_keys).difference(cfg_mongo.keys()))}"
        )
    return ms
