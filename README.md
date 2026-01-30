
# Setup

## Create a job:

- job/jobX.json

## Setup the job

```
{
    "root": "/Users/ab/Documents/python/IA",
    "prompts": [
        {
            "text": "Text of the prompt",
            "think": bool,
            "commit": null -> do not attempt to commit | true -> commit and expect changes | false -> check no changes,
            "next_on_fail": diff between current prompt index and target prompt if commit fails,
            "context": list of bool, one for each previous prompt. If true, that prompt will be considered. null for first prompt
            "tools": true to permit tool use,
            "permit_end": if model can end, if the model decide to not end the 'next_on_fail' is applied
        }
        ...
    ]
}
```

## Setup settings.json:

```
{
    "job_name": "name of the job file with no .json extension",
    "model": "model in ollama",
    "response_path": "file to log the responde, (e.g response.md)",
    "workspace_path": "ai's workspace directory, absolute path",
    "ignore_files": ["list files and directories names to ignore"]
}
```

# Setup python

```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

# Execute

> python3 main.py