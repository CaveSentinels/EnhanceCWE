from django.dispatch import Signal
''' This file contains a list of all the signals which can be invoked whenever required
These signals are handled by the emailer App
For the implementation of each of these signals, see the emailer app, models.py file
To call these signal, invoke it as signal_name.send(sender="", feedback="")
'''

# Sent when the review accepts the MUO
muo_accepted = Signal(providing_args=["instance"])

# Sent when the reviewer rejects a MUO
muo_rejected = Signal(providing_args=["instance"])


# Sent when the MUO has been voted up
muo_voted_up = Signal(providing_args=["instance"])


# Sent when the MUO has been voted down
muo_voted_down = Signal(providing_args=["instance"])


# Sent when the MUO has been marked as duplicate
muo_duplicate = Signal(providing_args=["instance"])


# Sent when the MUO has been marked as inappropriate
muo_inappropriate = Signal(providing_args=["instance"])


# Sent when the MUO has been submitted for review
muo_submitted_for_review = Signal(providing_args=["instance"])


# Sent when the muo is created
custom_muo_created = Signal(providing_args=["instance"])


# Sent when the custom muo gets promoted as generic muo
custom_muo_promoted_generic = Signal(providing_args=["instance"])

