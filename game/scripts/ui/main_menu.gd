extends Control
## Presentation only. No world truth or gameplay state is loaded into the menu.

var status_label: Label
var example_button: Button
var details: AcceptDialog

func _ready() -> void:
	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "top", "right", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 56)
	add_child(margin)
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 20)
	margin.add_child(column)
	add_label(column, "A U T O C I N E M A   /   DEVELOPMENT BUILD", 16, Color("7abcb8"))
	var spacer := Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	column.add_child(spacer)
	add_label(column, "Every story leaves a trace.", 42, Color("e7e5dd"))
	add_label(column, "Turn an original premise into a cinematic mystery.", 20, Color("a6b5bd"))
	add_label(column, "BLACKWATER HARBOR  /  THE KEEPER'S LIGHT", 18, Color("d1b681"))
	add_label(column, "A lighthouse glows twenty years after its keeper vanished.", 18, Color("a6b5bd"))
	var buttons := HBoxContainer.new()
	buttons.add_theme_constant_override("separation", 16)
	column.add_child(buttons)
	example_button = Button.new()
	example_button.text = "About the reference mystery"
	example_button.custom_minimum_size = Vector2(300, 52)
	example_button.pressed.connect(_show_example)
	buttons.add_child(example_button)
	var quit_button := Button.new()
	quit_button.text = "Quit"
	quit_button.custom_minimum_size = Vector2(100, 52)
	quit_button.pressed.connect(func() -> void: get_tree().quit())
	buttons.add_child(quit_button)
	status_label = add_label(column, "MILESTONE 0  /  Menu and world contracts. Gameplay is not available yet.", 16, Color("a6b5bd"))
	details = AcceptDialog.new()
	details.title = "Blackwater Harbor - reference world"
	details.dialog_text = "Five locations. Three characters. A mystery built around evidence.\n\nThe reference JSON can be validated with the Python tools.\nPlayable exploration arrives after the Reality Engine foundation."
	add_child(details)
	example_button.grab_focus()

func add_label(parent: Node, text: String, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	parent.add_child(label)
	return label

func _show_example() -> void:
	details.popup_centered(Vector2i(620, 220))
