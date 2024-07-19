# from EduSmart.settings import AZURE_ACCOUNT_NAME, AZURE_ACCOUNT_KEY, AZURE_IMAGE_CONTAINER
# from storages.backends.azure_storage import AzureStorage
#
#
# class AzureMediaStorage(AzureStorage):
#     account_name = AZURE_ACCOUNT_NAME
#     account_key = AZURE_ACCOUNT_KEY
#     azure_container = AZURE_IMAGE_CONTAINER  # For image container by default
#
#     def __init__(self, account_name=None, account_key=None, azure_container=None, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if account_name:
#             self.account_name = account_name
#         if account_key:
#             self.account_key = account_key
#         if azure_container:
#             self.azure_container = azure_container