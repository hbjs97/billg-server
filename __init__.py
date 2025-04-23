import os
import logging

from billg.util import Vault


logging.basicConfig(level=logging.INFO)

profile = os.environ.get("PYTHON_ENV", "local")
if profile == "local":
    import dotenv

    dotenv.load_dotenv()
else:
    Vault.load(
        url="http://vault.example.com:8200",
        app="server",
        profile=profile,
    )
