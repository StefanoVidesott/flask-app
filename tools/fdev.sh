#! /bin/bash

# Source the fdev_actions.sh file
source ./tools/fdev_actions.sh

# Define custom commands
fdev() {
  local action=$1
  shift
  case "$action" in
    help)
      _usage
      ;;
    compose)
      local compose_action=$1
      shift
      case "$compose_action" in
        start)
          _start_compose
          ;;
        stop)
          _stop_compose
          ;;
        restart)
          _stop_compose
          _start_compose
          ;;
        remove)
          _remove_compose
          ;;
        build)
          _build_compose
          ;;
        logs)
          _logs_compose
          ;;
        *)
          echo "Unknown compose action: $compose_action"
          _usage
          return 1
          ;;
      esac
      ;;
    flask)
      local flask_action=$1
      shift
      case "$flask_action" in
        start)
          _start_flask
          ;;
        stop)
          _stop_flask
          ;;
        restart)
          _stop_flask
          _start_flask
          ;;
        logs)
          _logs_flask
          ;;
        bash)
          _bash_flask
          ;;
        shell)
          _shell_flask
          ;;
        *)
          echo "Unknown flask action: $flask_action"
          _usage
          return 1
          ;;
      esac
      ;;
    db)
      local db_action=$1
      shift
      case "$db_action" in
        start)
          _start_db
          ;;
        stop)
          _stop_db
          ;;
        restart)
          _stop_db
          _start_db
          ;;
        logs)
          _logs_db
          ;;
        mysql)
          _mysql_db
          ;;
        upgrade)
          _upgrade_db
          ;;
        *)
          echo "Unknown db action: $db_action"
          _usage
          return 1
          ;;
      esac
      ;;
    *)
      echo "Unknown action: $action"
      _usage
      return 1
      ;;
  esac
}

# Completion function for 'fdev' command
_fdev_completions() {
  local cur prev words cword
  _init_completion || return

  local commands="compose flask db"
  local compose_commands="start stop restart remove build logs"
  local flask_commands="start stop restart logs bash shell"
  local db_commands="start stop restart logs mysql upgrade"

  if [[ ${cword} -eq 1 ]]; then
    COMPREPLY=( $(compgen -W "$commands" -- "$cur") )
    return 0
  elif [[ ${cword} -eq 2 && "${COMP_WORDS[1]}" == "compose" ]]; then
    COMPREPLY=( $(compgen -W "$compose_commands" -- "$cur") )
    return 0
  elif [[ ${cword} -eq 2 && "${COMP_WORDS[1]}" == "flask" ]]; then
    COMPREPLY=( $(compgen -W "$flask_commands" -- "$cur") )
    return 0
  elif [[ ${cword} -eq 2 && "${COMP_WORDS[1]}" == "db" ]]; then
    COMPREPLY=( $(compgen -W "$db_commands" -- "$cur") )
    return 0
  fi
}

# Register the completion function
complete -F _fdev_completions fdev

# Display usage by default if the script is sourced
_usage
