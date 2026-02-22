from pywinauto import Application

# Connect to an existing application
app = Application().connect(title="BlueStacks App Player 1")
window = app.window(title="BlueStacks App Player 1")

# Get the rectangle coordinates
rect = window.rectangle()
print(f"Rectangle: {rect}")
print(f"Left: {rect.left}, Top: {rect.top}, Right: {rect.right}, Bottom: {rect.bottom}")
