
UNIT_TYPE_CHOICES = [
    ("", "Select unit type"),
    ("Bedsitter", "Bedsitter"),
    ("Single room", "Single room"),
    ("Double room", "Double room"),
    ("Studio", "Studio"),
    ("One bedroom", "One bedroom"),
    ("Two bedroom", "Two bedroom"),
    ("Three bedroom", "Three bedroom"),
    ("Four bedroom", "Four bedroom"),
    ("Shop", "Shop"),
    ("Office", "Office"),
    ("Warehouse", "Warehouse"),
    ("Other", "Other"),
]

COMMON_UNIT_TYPES = {
    value
    for value, label in UNIT_TYPE_CHOICES
    if value and value != "Other"
}
