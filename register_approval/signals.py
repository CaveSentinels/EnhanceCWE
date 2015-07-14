from django.dispatch import Signal

# Sent when the registration request is approved
register_approved = Signal(providing_args=["instance"])

# Sent when the registration request is rejected
register_rejected = Signal(providing_args=["instance"])
