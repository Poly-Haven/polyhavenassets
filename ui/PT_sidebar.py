import bpy
import textwrap
import logging
from .. import ephemeral
from .. import icons
from ..utils.dpi_factor import dpi_factor
from ..utils.early_access import early_access
from .. import addon_updater_ops

log = logging.getLogger(__name__)


def paragraph(text, width, layout, align="CENTER"):
    wrapp = textwrap.TextWrapper(width=round(width / 6.5))
    layout.separator()
    textcol = layout.column(align=True)
    textcol.scale_y = 0.7
    for line in text.split("\n"):
        if not line:
            textcol.separator()
            continue
        for wrapped in wrapp.wrap(text=line):
            row = textcol.row(align=True)
            row.alignment = align
            row.label(text=wrapped)


def _is_valid_builtin_icon(name):
    try:
        enum_items = bpy.types.UILayout.bl_rna.functions["operator"].parameters["icon"].enum_items
        return name in enum_items
    except (KeyError, AttributeError):
        return False


def _operator_exists(idname):
    try:
        category, name = idname.split(".", 1)
        return hasattr(getattr(bpy.ops, category), name)
    except (ValueError, AttributeError):
        return False


def _news_button_icon_kwargs(icon, icons_coll):
    """Resolve a news button icon: bundled icon file first, then a built-in icon
    name, else nothing (failing silently with a warning)."""
    if not icon:
        return {}
    if icon in icons_coll:
        return {"icon_value": icons_coll[icon].icon_id}
    if _is_valid_builtin_icon(icon):
        return {"icon": icon}
    log.warning(f"News button icon '{icon}' is neither a bundled icon nor a built-in Blender icon")
    return {}


def draw_news(layout, context, news_item):
    i = icons.get_icons()
    box = layout.box()
    col = box.column(align=True)

    header = col.row(align=True)
    header.label(text=news_item.get("title", ""), icon_value=i["polyhaven"].icon_id)
    header.operator("pha.dismiss_news", text="", icon="PANEL_CLOSE", emboss=False).key = news_item.get("key", "")

    content = news_item.get("content", "")
    if content:
        width = context.region.width / dpi_factor()
        align = "LEFT" if news_item.get("align") == "left" else "CENTER"
        paragraph(content, width, col, align=align)

    button = news_item.get("button")
    if button and button.get("text") and button.get("target"):
        col.separator()
        text = button["text"]
        target = button["target"]
        kwargs = _news_button_icon_kwargs(button.get("icon"), i)
        if target.startswith("http"):
            col.operator("wm.url_open", text=text, **kwargs).url = target
        elif _operator_exists(target):
            col.operator(target, text=text, **kwargs)
        else:
            log.warning(f"News button target '{target}' is not a URL or a known operator; skipping button")


class PHA_PT_sidebar(bpy.types.Panel):

    bl_label = "Poly Haven"
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOLS"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(self, context):
        lib_ref = getattr(context.space_data.params, "asset_library_ref", None)  # Blender < 4.0
        lib_ref = getattr(context.space_data.params, "asset_library_reference", lib_ref)  # Blender > 4.0
        return context.area.ui_type == "ASSETS" and lib_ref.lower() == "poly haven"

    def draw(self, context):
        addon_updater_ops.check_for_update_background()
        layout = self.layout

        if ephemeral.recently_downloaded:
            box = layout.box()
            col = box.column(align=True)
            row = col.row()
            row.label(text="Recently downloaded:", icon="IMPORT")
            if context.space_data.params.filter_search:
                row.operator("pha.go_to_asset", text="Clear Search", icon="PANEL_CLOSE").asset = ""
            list_size = 10
            recently_downloaded = list(reversed(ephemeral.recently_downloaded))
            for asset in (
                recently_downloaded
                if context.window_manager.pha_props.show_more_recent
                else recently_downloaded[:list_size]
            ):
                row = col.row(align=True)
                row.alignment = "RIGHT"
                row.operator("pha.go_to_asset", text=f"{asset} →", emboss=False).asset = asset
            if len(recently_downloaded) > list_size:
                col.prop(
                    context.window_manager.pha_props,
                    "show_more_recent",
                    text="",
                    icon="TRIA_UP" if context.window_manager.pha_props.show_more_recent else "TRIA_DOWN",
                )
            layout.separator()

        if not early_access:  # We don't need to nag existing supporters :)
            i = icons.get_icons()
            col = layout.column()
            sidebar_width = 10000
            for region in context.area.regions:
                if region.type == "TOOLS":
                    sidebar_width = region.width / dpi_factor()
            row = col.row()
            row.alignment = "CENTER"
            row.scale_y = 1.5
            row.operator("wm.url_open", text="Support us!", icon_value=i["heart"].icon_id).url = (
                "https://www.patreon.com/polyhaven/overview"
            )
            paragraph(
                (
                    "You might have downloaded this add-on for free, but Poly Haven needs funds to continue "
                    "creating assets for you :)"
                ),
                sidebar_width,
                col,
            )
            paragraph(
                (
                    "Please support our work by purchasing this add-on on the "
                    "Blender Market or by supporting us on Patreon."
                ),
                sidebar_width,
                col,
            )
            col.separator()

        addon_updater_ops.update_notice_box_ui(self, context)

        if ephemeral.news_item:
            draw_news(layout, context, ephemeral.news_item)
