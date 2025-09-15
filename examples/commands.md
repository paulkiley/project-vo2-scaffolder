# Examples: Common Commands

Build and validate the manifest:

```
just db
just validate
just verify
```

Populate the files into the current directory:

```
mkdir -p ./playground && cd ./playground
python3 ../02-populate-files.py
```

Render templates using a YAML context:

```
# Minimal context
just render CONTEXT=../examples/context-minimal.yaml OUT=./rendered

# Strict mode with a richer context
just render-strict CONTEXT=../examples/context-full.yaml OUT=./rendered
```

Copy the scaffold as a new project via Copier:

```
just copier DEST=../my-new-project
```

