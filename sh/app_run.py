# -*- coding: utf-8 -*-

"""
.. module:: app_run.py
   :license: GPL/CeCIL
   :platform: Unix, Windows
   :synopsis: Runs the web-service.

.. moduleauthor:: Mark A. Greenslade

"""
import sys
import errata as APP



def _main():
    """Main entry point.

    """
    # Run web service.
    try:
        APP.run()

    # Handle unexpected exceptions.
    except Exception as err:
        # Ensure that web-service is stopped.
        try:
            APP.stop()
        except:
            pass

        # Ensure that all active db transactions are cancelled.
        try:
            APP.db.session.rollback()
        except:
            pass

        # Simple log to stdout.
        print err

    # Signal exit.
    finally:
        sys.exit()


# Main entry point.
if __name__ == '__main__':
    _main()
