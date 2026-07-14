import bpy
import logging
from ..utils import news
from .. import ephemeral

log = logging.getLogger(__name__)


class PHA_OT_dismiss_news(bpy.types.Operator):
    bl_idname = "pha.dismiss_news"
    bl_label = "Dismiss"
    bl_description = "Dismiss this announcement. It won't be shown again"
    bl_options = {"INTERNAL"}

    key: bpy.props.StringProperty()

    def execute(self, context):
        news.dismiss(self.key)
        ephemeral.news_item = None
        return {"FINISHED"}
