from django.dispatch import Signal
''' This file contains a list of all the signals which can be invoked whenever required
These signals are handled by the muo_mailer App
For the implementation of each of these signals, see the muo_mailer app, models.py file
To call these signal, invoke it as signal_name.send(sender="", feedback="")
'''

# Sent when the review accepts the MUO
cwe_created = Signal(providing_args=["instance"])
