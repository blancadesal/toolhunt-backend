from tortoise import fields, models


class User(models.Model):
    id = fields.CharField(max_length=255, pk=True)
    username = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)
    encrypted_token = fields.BinaryField(null=True)
    token_expires_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users"


class Tool(models.Model):
    name = fields.CharField(max_length=255, pk=True)
    title = fields.CharField(max_length=255, null=False)
    description = fields.TextField(null=False)
    url = fields.CharField(max_length=2047, null=False)
    last_updated = fields.DatetimeField(auto_now=True)
    deprecated = fields.BooleanField(default=False)
    experimental = fields.BooleanField(default=False)

    tasks: fields.ReverseRelation["Task"]
    completed_tasks: fields.ReverseRelation["CompletedTask"]

    class Meta:
        table = "tool"
        charset = "binary"


class Task(models.Model):
    id = fields.IntField(pk=True)
    tool = fields.ForeignKeyField(
        "models.Tool", related_name="tasks", on_delete=fields.CASCADE
    )
    field = fields.CharField(max_length=80, null=False)
    last_attempted = fields.DatetimeField(null=True)
    times_attempted = fields.IntField(default=0)
    last_updated = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "task"
        unique_together = ("tool", "field")
        charset = "binary"


class CompletedTask(models.Model):
    id = fields.IntField(pk=True, generated=True)
    tool = fields.ForeignKeyField(
        "models.Tool",
        related_name="completed_tasks",
        on_delete=fields.SET_NULL,
        null=True,
    )
    tool_title = fields.CharField(max_length=255, null=False)
    field = fields.CharField(max_length=80, null=False)
    user = fields.CharField(max_length=255, null=False)
    completed_date = fields.DatetimeField(null=False)

    class Meta:
        table = "completed_task"
        charset = "binary"
