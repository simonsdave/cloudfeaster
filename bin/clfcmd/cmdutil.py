"""This module contains a small collection of utilities that are
used across a variety of commands."""

def create_command_to_function_dict(command_names, function):
    return {command_name: function for command_name in command_names}
