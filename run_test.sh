#!/usr/bin/env bash

echo "This script tests the project."

# Run the unit tests
python manage.py test cwe muo --settings=EnhancedCWE.test_settings