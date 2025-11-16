"""
Models for RepairRequestArchives compatibility layer.

RepairRequestArchive uses the RepairRequest model with is_archived=True filter.
No separate model needed - archives are just archived repair requests.
"""
from zistino_apps.compatibility.repairrequests.models import RepairRequest

__all__ = ['RepairRequest']

