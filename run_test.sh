#!/usr/bin/env bash

echo "This script tests the project."

# Run the "cwe" tests
ret = $(python manage.py test cwe --settings=EnhancedCWE.test_settings)
echo $ret

# Run the "muo" tests
ret = $(python manage.py test muo --settings=EnhancedCWE.test_settings)
echo $ret