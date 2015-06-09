#!/usr/bin/env bash

echo "This script tests the project."

# Run the "cwe" tests
python manage.py test cwe --settings=EnhancedCWE.test_settings

# Run the "muo" tests
python manage.py test muo --settings=EnhancedCWE.test_settings