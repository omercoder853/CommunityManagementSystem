from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def _safe_send(subject, message, recipient):
    """Ortak gönderim yardımcısı — hatayı loglar, sessizce yutmaz."""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
    except Exception as exc:
        logger.error("E-posta gönderilemedi → %s | Hata: %s", recipient, exc)


def send_advisor_request_email(advisor, requester, community_name):
    """E-posta: Danışmana topluluk kurma isteği bildir."""
    subject = f"[CommHub] Yeni Danışmanlık Talebi: {community_name}"
    message = (
        f"Sayın {advisor.get_full_name()},\n\n"
        f"{requester.get_full_name()} adlı öğrenci \"{community_name}\" topluluğunu kurmak için "
        f"sizden danışmanlık talebinde bulundu.\n\n"
        f"Sisteme giriş yaparak bu talebi inceleyebilir, kabul ya da reddedebilirsiniz.\n\n"
        f"CommHub | Topluluk Yönetim Sistemi"
    )
    _safe_send(subject, message, advisor.email)


def send_request_accepted_email(requester, community_name):
    """E-posta: Öğrenciye topluluk talebinin onaylandığını bildir."""
    subject = f"[CommHub] Topluluk Talebiniz Onaylandı: {community_name}"
    message = (
        f"Sayın {requester.get_full_name()},\n\n"
        f"Danışman hoca \"{community_name}\" topluluğu için danışmanlık talebinizi onayladı. "
        f"Topluluk başarıyla kurulmuş olup siz topluluk başkanı olarak atandınız.\n\n"
        f"CommHub | Topluluk Yönetim Sistemi"
    )
    _safe_send(subject, message, requester.email)


def send_request_rejected_email(requester, community_name, reason=""):
    """E-posta: Öğrenciye topluluk talebinin reddedildiğini bildir."""
    subject = f"[CommHub] Topluluk Talebiniz Reddedildi: {community_name}"
    reason_line = f"\nGerekçe: {reason}\n" if reason else ""
    message = (
        f"Sayın {requester.get_full_name()},\n\n"
        f"Danışman hoca \"{community_name}\" topluluğu için danışmanlık talebinizi reddetti."
        f"{reason_line}\n\n"
        f"CommHub | Topluluk Yönetim Sistemi"
    )
    _safe_send(subject, message, requester.email)


def send_join_notification_email(director, student, community_name):
    """E-posta: Başkana yeni üyelik talebi bildir."""
    subject = f"[CommHub] Yeni Üyelik Talebi: {community_name}"
    message = (
        f"Sayın {director.get_full_name()},\n\n"
        f"{student.get_full_name()} adlı öğrenci \"{community_name}\" topluluğuna katılmak istediğini bildirdi.\n\n"
        f"Sisteme giriş yaparak bu talebi yönetebilirsiniz.\n\n"
        f"CommHub | Topluluk Yönetim Sistemi"
    )
    _safe_send(subject, message, director.email)
