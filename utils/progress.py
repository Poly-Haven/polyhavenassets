import math


def init(context, num_items, word="Progress"):
    props = context.window_manager.pha_props
    props.progress_word = word
    props.progress_total = num_items
    props.progress_percent = 0


def update(context, prog, text=None):
    props = context.window_manager.pha_props
    props.progress_percent = math.floor(prog / max(1, props.progress_total) * 100)
    context.workspace.status_text_set_internal(text)  # Forces statusbar redraw
    for a in context.screen.areas:
        if a.type == "PROPERTIES":
            a.tag_redraw()


def end(context):
    props = context.window_manager.pha_props
    props.progress_percent = 0
    props.progress_total = 0
    context.workspace.status_text_set_internal(None)  # Forces statusbar redraw, remove text
    for a in context.screen.areas:
        if a.type == "PROPERTIES":
            a.tag_redraw()
