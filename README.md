
# Setup

## Setup model:

- Use ollama to host the model
- Consider to use the Modelfile provided [Modelfile](./Modefile)

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
    "use_git": true to use git version control,
    "existing_branch": null to create new or "the name of the folder in the worspace to work in",
    "model": "model pulled in ollama",
    "response_path": "relative path in the target for all ia response log data",
    "workspace_path": "absolute path for ai's workspace directory",
    "ignore_files": ["list of files and directories names to ignore"]
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