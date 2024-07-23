# Flask application

### Enabling the development environment

Must add the following alias to the `.bashrc` file filling the `<project_root>` with the path to the project root directory.

```bash
alias fenv="cd '<project_root>' 1>/dev/null 2>&1; [[ -f ./fenv.sh ]] && { echo -en '\nActivating fenv...\n' && source ./fenv.sh ; } || { echo -en '\n?project root not valid.\n' ; }"
```

### Development environment usage

To activate the development environment, run the following command in the terminal:

```bash
fenv
```