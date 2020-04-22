from ma import ma
from models.confirmation import ConfirmationModel


class ItemSchema(ma.ModelSchema):
    class Meta:
        model = ConfirmationModel
        load_only = ("user",)
        dump_only = ("id", "expired_at", "confirmed")
        include_fk = True
