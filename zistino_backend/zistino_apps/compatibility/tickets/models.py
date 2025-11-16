"""
Models for Tickets compatibility layer.
"""
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Ticket(models.Model):
    """Ticket model matching old Swagger format."""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets', help_text='Ticket creator')
    subject = models.CharField(max_length=255, help_text='Ticket subject')
    status = models.IntegerField(default=0, help_text='Ticket status (0=open, 1=closed, etc.)')
    priority = models.IntegerField(default=0, help_text='Ticket priority (0=low, 1=medium, 2=high, 3=urgent)')
    category_id = models.IntegerField(null=True, blank=True, default=None, help_text='Category ID')
    item_id = models.IntegerField(null=True, blank=True, default=None, help_text='Item ID')
    item_type = models.IntegerField(default=0, help_text='Item type')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tickets'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.id}: {self.subject}"


class TicketMessage(models.Model):
    """Ticket message model matching old Swagger format."""
    id = models.AutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='ticket_messages', help_text='Related ticket')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_messages', help_text='Message sender')
    message = models.TextField(help_text='Message content')
    type = models.IntegerField(default=0, help_text='Message type (0=user, 1=admin, etc.)')
    status = models.IntegerField(default=0, help_text='Message status')
    response_message_id = models.IntegerField(null=True, blank=True, default=None, help_text='Response to message ID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ticket_messages'
        verbose_name = 'Ticket Message'
        verbose_name_plural = 'Ticket Messages'
        ordering = ['created_at']

    def __str__(self):
        return f"Message #{self.id} for Ticket #{self.ticket.id}"


class TicketMessageDocument(models.Model):
    """Ticket message document model matching old Swagger format."""
    id = models.AutoField(primary_key=True)
    ticket_message = models.ForeignKey(TicketMessage, on_delete=models.CASCADE, related_name='ticket_message_documents', help_text='Related ticket message')
    file_url = models.CharField(max_length=500, help_text='File URL')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ticket_message_documents'
        verbose_name = 'Ticket Message Document'
        verbose_name_plural = 'Ticket Message Documents'
        ordering = ['created_at']

    def __str__(self):
        return f"Document #{self.id} for Message #{self.ticket_message.id}"
