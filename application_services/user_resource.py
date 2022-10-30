from application_services.BaseApplicationResource import BaseRDBApplicationResource
from database_services.RDBService import RDBService

class UserResource(BaseRDBApplicationResource):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_all_users(cls, template):
        return RDBService.find_by_template("users", "user", template)

    @classmethod
    # db_schema, table_name, column_list, value_list
    def add_by_user_attributes(cls, column_name_list, value_list):
        return RDBService.insert("users", "user", column_name_list, value_list, return_id=True)

    @classmethod
    def delete_by_user_id(cls, user_id):
        return RDBService.delete_by_column("users", "user", "user_id", user_id)

    @classmethod
    def get_by_user_id(cls, user_id):
        return RDBService.find_by_template("users", "user", {"user_id": user_id})

    @classmethod
    def update_by_user_id(cls, user_id, column_name, value):
        return RDBService.update_by_column("users", "user", "user_id", user_id, column_name, value)

    @classmethod
    def update_by_user_id(cls, user_id, **kwargs):
        return RDBService.update_by_template("users", "user", {'user_id': user_id}, kwargs)

    @classmethod
    def exists_by_email(cls, email):
        return len(RDBService.get_by_value("users", "user", "email", email)) > 0

    @classmethod
    def get_user_id_by_email(cls, email):
        res = RDBService.find_by_template("users", "user", {'email': email}, ['user_id'])
        return res if len(res) != 0 else None