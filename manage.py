import os
import socket
import sys

if __name__ == "__main__":
    if socket.gethostname() == "master":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.dev")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.pro")

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django."
                "Are you sure it's installed and available on your python path environment variable?"
                "Did you forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
