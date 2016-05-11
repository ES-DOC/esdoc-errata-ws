# -*- coding: utf-8 -*-

"""
.. module:: run_web_service.py
   :license: GPL/CeCIL
   :platform: Unix, Windows
   :synopsis: Runs the errata web-service.

.. moduleauthor:: Atef Benasser <abenasser@ipsl.jussieu.fr>

"""
import sys
import errata



def _main():
    """Main entry point.

    """
    # Run web service.
    try:
        errata.run()

    # Handle unexpected exceptions.
    except Exception as err:
        # Simple log to stdout.
        print err

        # Ensure that web-service is stopped.
        try:
            errata.stop()
        except:
            pass

        # Ensure that all active db transactions are cancelled.
        try:
            errata.db.session.rollback()
        except:
            pass

    # Signal exit.
    finally:
        sys.exit()


# Main entry point.
if __name__ == '__main__':
    _main()
