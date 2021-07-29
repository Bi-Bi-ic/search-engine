from marshmallow import Schema, fields, RAISE, post_dump
class ImageSchema(Schema):
    """
    Image Factory
    """

    SKIP_VALUES = set([None, ""])

    id = fields.UUID(required=True, dump_only=True)
    created_at = fields.Int(required=True, dump_only=True)
    link = fields.String(required=True ,dump_only=True)

    class Meta:
        strict = True
        unknown = RAISE
        ordered = True
class SearchView(Schema):
    """
    View Factory
    """

    SKIP_VALUES = set([None, ""])

    persent = fields.Float(required=True, dump_only=True)
    id = fields.UUID(required=True, dump_only=True)
    created_at = fields.Int(required=True, dump_only=True)
    link = fields.String(required=True ,dump_only=True)

    class Meta:
        strict = True
        unknown = RAISE
        ordered = True
