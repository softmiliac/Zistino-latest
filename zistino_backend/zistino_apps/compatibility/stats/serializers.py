"""
Serializers for Stats endpoints.
Stats endpoints typically return aggregated data, so serializers are minimal.
"""
from rest_framework import serializers

# Stats endpoints return aggregated data, so we don't need complex request serializers
# The responses are typically dictionaries with statistics

