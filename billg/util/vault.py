import hvac
import os


class Vault:
    def __init__(self, url: str, token: str):
        self.client = hvac.Client(
            url=url,
            token=token,
        )
        self._secrets: dict = {}

    @staticmethod
    def load(
        url: str,
        app: str,
        profile: str,
        mount_point: str = "billg",
        token: str = os.environ.get("VAULT_TOKEN", ""),
    ):
        vault = Vault(url, token)
        vault.read_kv2(app=app, profile=profile, mount_point=mount_point)
        vault.copy_to_env()

    def read_kv2(
        self,
        app: str,
        profile: str,
        mount_point: str = "billg",
    ):
        try:
            secret_response = self.client.secrets.kv.v2.read_secret_version(
                mount_point=mount_point,
                path=f"{app}/{profile}",
            )
        except Exception as e:
            print(
                f"An error occurred while trying to read secret at path '{mount_point}/{app}/{profile}'"
            )
            raise e
        self._secrets = secret_response["data"]["data"]

    def copy_to_env(self):
        for key, value in self._secrets.items():
            os.environ[key] = value
