import os
import sys


def main():
    """
    Run administrative tasks for the SmartFM Django application.

    Sets the Django settings module to smartfm_project.settings
    and executes the command passed via the command line.
    """
    # Tell Django which settings file to use
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "smartfm_project.settings"
    )

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Could not import Django. "
            "Make sure Django 4.2 is installed by running:\n"
            "    pip3 install 'django==4.2'\n"
            "Then try running this command again."
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()