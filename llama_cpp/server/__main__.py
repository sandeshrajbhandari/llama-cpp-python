"""Example FastAPI server for llama.cpp.

To run this example:

```bash
pip install fastapi uvicorn sse-starlette
export MODEL=../models/7B/...
```

Then run:
```
uvicorn llama_cpp.server.app:app --reload
```

or

```
python3 -m llama_cpp.server
```

Then visit http://localhost:8000/docs to see the interactive API docs.

"""
import os
import argparse

import uvicorn
from pyngrok import ngrok, conf
import nest_asyncio

from llama_cpp.server.app import create_app, Settings

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name, field in Settings.__fields__.items():
        description = field.field_info.description
        if field.default is not None and description is not None:
            description += f" (default: {field.default})"
        parser.add_argument(
            f"--{name}",
            dest=name,
            type=field.type_,
            help=description,
        )

    parser.add_argument(
            f"--use_ngrok",
            type=bool,
            help="use ngrok public url or not",
        )
    args = parser.parse_args()
    ## if args has use_ngrok value then remove it from args array
    use_ngrok = False ## default
    k_v_dict = {k: v for k, v in vars(args).items() if v is not None}
    ## remove use_ngrok from k_v_dict before passing to Settings
    ## Encountered Settings validation error when passing use_ngrok to Settings
    ## write a better implementation to use ngrok if possible.
    if "use_ngrok" in k_v_dict:
        use_ngrok = k_v_dict["use_ngrok"]
        del k_v_dict["use_ngrok"] ## del keyword is used to delete a key from dictionary
        ## set "host" to "127.0.0.1" and port to 2600 if use_ngrok is True
        if use_ngrok:
            print ("changing host and port to 127.0.0.1 and 2600 for using with ngrok in colab")
            k_v_dict["host"] = "127.0.0.1"
            k_v_dict["port"] = 2600
    settings = Settings(**k_v_dict)

    app = create_app(settings=settings)

    ## ngrok condition.
    if use_ngrok:
        import getpass
        print("Enter your authtoken, which can be copied from https://dashboard.ngrok.com/auth")
        conf.get_default().auth_token = getpass.getpass()

        ngrok_tunnel = ngrok.connect(int(os.getenv("PORT", settings.port)))
        print('Public URL:', ngrok_tunnel.public_url)
        print(f'Go to {ngrok_tunnel.public_url}/docs to see the interactive API docs.')
        nest_asyncio.apply()
    ##
    uvicorn.run(
        app, host=os.getenv("HOST", settings.host), port=int(os.getenv("PORT", settings.port))
    )
