from tortoise import fields, models


class User(models.Model):
    id = fields.CharField(max_length=255, pk=True)
    username = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)
    token = fields.JSONField(null=True)
    token_expires_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users"

