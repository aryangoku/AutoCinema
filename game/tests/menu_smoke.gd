extends SceneTree

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var packed := load("res://scenes/app/MainMenu.tscn") as PackedScene
	if packed == null:
		push_error("Main menu scene could not load")
		quit(1)
		return
	var menu := packed.instantiate()
	root.add_child(menu)
	await process_frame
	if menu.example_button == null or menu.status_label == null:
		push_error("Main menu controls are missing")
		quit(1)
		return
	menu.example_button.pressed.emit()
	await process_frame
	if not menu.details.visible:
		push_error("Reference mystery information did not open")
		quit(1)
		return
	menu.details.hide()
	print("PASS: menu loads, controls exist, reference dialog opens and closes")
	quit(0)
