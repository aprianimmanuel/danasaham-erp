from __future__ import annotations

from django.core.mail.backends.smtp import EmailBackend
import ssl
import smtplib


class CustomTLSBackend(EmailBackend):
    # def __init__(self, *args, **kwargs):
    #     self.local_hostname = kwargs.pop("local_hostname", None)
    #     super().__init__(*args, **kwargs)

    def open(self) -> bool:
        """Open a connection to the SMTP server.

        Returns:
        -------
        bool
            True if the connection is successfully opened, False otherwise.

        Raises:
        ------
        Exception
            If an error occurs and `fail_silently` is False.
        """
        if self.connection:
            return False

        connection_class = smtplib.SMTP

        try:
            self.connection = connection_class(
                self.host,
                self.port,
                timeout=self.timeout,
            )

            if self.use_tls:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

                self.connection.starttls(context=context)

            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True

        except Exception:
            if self.fail_silently:
                return False
            raise
