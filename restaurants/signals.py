"""
Restaurants Signals
"""
###
# Libraries
###
from django.db.models.signals import post_save
from django.dispatch import receiver

from restaurants.models import StatusHistory


###
# Signals
###
@receiver(
    post_save,
    sender=StatusHistory,
    dispatch_uid='update_order_status'
)
def update_order_status(sender, instance, created, **kwargs):
    order = instance.order
    order.status = instance.status
    order.save(update_fields=['status'])
