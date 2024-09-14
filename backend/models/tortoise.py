from tortoise import fields, models


class User(models.Model):
    id = fields.CharField(max_length=255, pk=True)
    username = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)
    token = fields.TextField(null=True)
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

    tasks: fields.ReverseRelation["Task"]
    completed_tasks: fields.ReverseRelation["CompletedTask"]

    class Meta:
        table = "tool"
        charset = "binary"


class Field(models.Model):
    name = fields.CharField(max_length=80, pk=True)
    description = fields.CharField(max_length=2047, null=False)
    input_options = fields.CharField(max_length=2047, null=True)
    pattern = fields.CharField(max_length=320, null=True)

    tasks: fields.ReverseRelation["Task"]
    completed_tasks: fields.ReverseRelation["CompletedTask"]

    class Meta:
        table = "field"
        charset = "binary"


class Task(models.Model):
    id = fields.IntField(pk=True)
    tool = fields.ForeignKeyField(
        "models.Tool", related_name="tasks", on_delete=fields.CASCADE
    )
    field = fields.ForeignKeyField("models.Field", related_name="tasks")
    last_attempted = fields.DatetimeField(null=True)
    times_attempted = fields.IntField(default=0)
    last_updated = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "task"
        unique_together = ("tool", "field")
        charset = "binary"


class CompletedTask(models.Model):
    id = fields.IntField(pk=True, generated=True)  # Ensure id is auto-incremented
    tool = fields.ForeignKeyField(
        "models.Tool",
        related_name="completed_tasks",
        on_delete=fields.SET_NULL,
        null=True,
    )
    tool_title = fields.CharField(max_length=255, null=False)
    field = fields.ForeignKeyField(
        "models.Field",
        related_name="completed_tasks",
        on_delete=fields.SET_NULL,
        null=True,
    )
    user = fields.CharField(max_length=255, null=False)
    completed_date = fields.DatetimeField(null=False)

    class Meta:
        table = "completed_task"
        charset = "binary"
