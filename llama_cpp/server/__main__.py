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
from pyngrok import ngrok
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
    ## remove use_ngrok from k_v_dict
    if "use_ngrok" in k_v_dict:
        use_ngrok = k_v_dict["use_ngrok"]
        del k_v_dict["use_ngrok"] ## del keyword is used to delete a key from dictionary
    settings = Settings(**k_v_dict)

    app = create_app(settings=settings)

    if use_ngrok:
        ngrok_tunnel = ngrok.connect(int(os.getenv("PORT", settings.port)))
        print('Public URL:', ngrok_tunnel.public_url)
        nest_asyncio.apply()
    uvicorn.run(
        app, host=os.getenv("HOST", settings.host), port=int(os.getenv("PORT", settings.port))
    )
