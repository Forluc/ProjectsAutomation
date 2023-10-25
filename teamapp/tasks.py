from celery import shared_task


@shared_task(bind=True, name="Add new Invitation")  # здесь bind=True, чтобы получить доступ к текущей задаче
def send_invitation_task(invitation_id):
    from .models import Invitation
    invitation = Invitation.objects.get(id=invitation_id)
