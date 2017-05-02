from django.contrib.auth.base_user import BaseUserManager
from django.db import models


class YalieManager(BaseUserManager):
    pass


class RideRequestManager(models.Manager):
    def create_ride_request(self, appointment, requester):
        ride_request = self.create(
            appointment=appointment,
            requester=requester,
        )
        return ride_request
