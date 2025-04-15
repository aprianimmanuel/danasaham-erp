from __future__ import annotations

import uuid

from django.conf import settings  #type: ignore  # noqa: PGH003
from django.db import models  #type: ignore   # noqa: PGH003
from django.utils.translation import gettext_lazy as _  # type: ignore   # noqa: PGH003

from app.documents.models import Document  #type: ignore  # noqa: PGH003


class dttotDoc(models.Model):  # noqa: N801
    updated_at = models.DateTimeField(
        _("DTTOT Updated at"),
        auto_now=True,
        null=True)
    last_update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="updated_dttot_docs",
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        related_name="dttotDocs",
        related_query_name="dttotDoc",
        null=True,
    )
    dttot_id = models.CharField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        max_length=36,
        unique=True,
        verbose_name=_("DTTOT ID"),
    )
    dttot_first_name = models.CharField(  # noqa: DJ001
        _("DTTOT First Name"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_middle_name = models.CharField(  # noqa: DJ001
        _("DTTOT Middle Name"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_last_name = models.CharField(  # noqa: DJ001
        _("DTTOT Last Name"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_1 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_1 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_1 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_1 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_2 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_2 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_2 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_2 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_3 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 3"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_3 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 3"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_3 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 3"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_3 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 3"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_4 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 4"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_4 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 4"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_4 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 4"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_4 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 4"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_5 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 5"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_5 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 5"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_5 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 5"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_5 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 5"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_6 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 6"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_6 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 6"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_6 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 6"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_6 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 6"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_7 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 7"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_7 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 7"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_7 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 7"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_7 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 7"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_8 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 8"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_8 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 8"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_8 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 8"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_8 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 8"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_9 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 9"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_9 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 9"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_9 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 9"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_9 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 9"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_10 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 10"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_10 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 10"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_10 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 10"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_10 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 10"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_11 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 11"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_11 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 11"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_11 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 11"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_11 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 11"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_12 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 12"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_12 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 12"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_12 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 12"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_12 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 12"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_13 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 13"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_13 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 13"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_13 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 13"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_13 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 13"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_14 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 14"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_14 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 14"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_14 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 14"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_14 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 14"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_15 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 15"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_15 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 15"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_15 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 15"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_15 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 15"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_16 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 16"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_16 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 16"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_16 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 16"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_16 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 16"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_17 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 17"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_17 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 17"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_17 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 17"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_17 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 17"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_18 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 18"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_18 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 18"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_18 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 18"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_18 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 18"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_19 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 19"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_19 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 19"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_19 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 19"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_19 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 19"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_20 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 20"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_20 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 20"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_20 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 20"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_20 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 20"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_21 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 21"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_21 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 21"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_21 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 21"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_21 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 21"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_22 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 22"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_22 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 22"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_22 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 22"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_22 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 22"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_23 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 23"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_23 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 23"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_23 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 23"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_23 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 23"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_24 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 24"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_24 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 24"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_24 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 24"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_24 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 24"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_25 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 25"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_25 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 25"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_25 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 25"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_25 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 25"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_26 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 26"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_26 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 26"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_26 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 26"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_26 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 26"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_27 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 27"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_27 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 27"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_27 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 27"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_27 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 27"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_28 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 28"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_28 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 28"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_28 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 28"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_28 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 28"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_type = models.CharField(  # noqa: DJ001
        _("DTTOT Type"),
        max_length=255,
        blank=True,
        null=True,

    )
    dttot_kode_densus = models.CharField(  # noqa: DJ001
        _("DTTOT Kode Densus"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_birth_place = models.CharField(  # noqa: DJ001
        _("DTTOT Birth Place"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_birth_date_1 = models.CharField(  # noqa: DJ001
        _("DTTOT Birth Date 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_birth_date_2 = models.CharField(  # noqa: DJ001
        _("DTTOT Birth Date 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_birth_date_3 = models.CharField(  # noqa: DJ001
        _("DTTOT Birth Date 3"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_nationality_1 = models.CharField(  # noqa: DJ001
        _("DTTOT Nationality 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_nationality_2 = models.CharField(  # noqa: DJ001
        _("DTTOT Nationality 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_domicile_address = models.TextField(  # noqa: DJ001
        _("DTTOT Domicile Address"),
        blank=True,
        null=True,
    )
    dttot_description_1 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 1"),
        blank=True,
        null=True,
    )
    dttot_description_2 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 2"),
        blank=True,
        null=True,
        )
    dttot_description_3 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 3"),
        blank=True,
        null=True,
    )
    dttot_description_4 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 4"),
        blank=True,
        null=True,
    )
    dttot_description_5 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 5"),
        blank=True,
        null=True,
    )
    dttot_description_6 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 1"),
        blank=True,
        null=True,
    )
    dttot_description_7 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 2"),
        blank=True,
        null=True,
        )
    dttot_description_8 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 3"),
        blank=True,
        null=True,
    )
    dttot_description_9 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 4"),
        blank=True,
        null=True,
    )
    dttot_nik_ktp = models.CharField(  # noqa: DJ001
        _("DTTOT NIK KTP"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_passport_number = models.CharField(  # noqa: DJ001
        _("DTTOT Passport Number"),
        max_length=255,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.dttot_first_name} {self.dttot_last_name} - {self.dttot_type}"