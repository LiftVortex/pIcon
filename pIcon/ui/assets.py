"""
Small embedded icons as base64 PNGs (24x24), minimalistic line shapes to avoid external files.
"""
import base64
import tkinter as tk

# Simple generated monochrome PNGs (base64). These are tiny placeholder icons.
# Names: 'icon', 'recent', 'batch', 'settings', 'theme', 'open', 'save', 'export'
ICON_DATA = {
    "icon": b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAW0lEQVRIie3UQQrAIBAF0f//0zY0i5cCk3Uq1bFQy2Ck0Vw0kYc2Wg8z4h3c8Jm0q1dWc0ZkTj8K0bW2eJ5d2i8sI6pV0wqB4l2wS1xJ2n0q1QfGm2Y0+9x9o0i0e3B5Tz3gL5u9G7t9A9eZc0k6kQmQAAAABJRU5ErkJggg==',
    "recent": b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAZElEQVRIie2UsQ2AIBBE3xJHh7k1kZb2m0Q8o8yYy0Xlq8m2sKqvF5l3m2sKpQf0k9F3s1UqgU1w7mYk5HhQZgQ5nM9G9Q4k4e2Y6V1gk0r0r0g6bC8B9cG3y1r0V4JH0p3f3f0Y4N7XWqf8Ax9Jf2Wb8Zb8dQ2q7G9gAAAABJRU5ErkJggg==',
    "batch": b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAaUlEQVRIie2UsQ2AIBBF3yQk9+1sJkq7J2JgXoZDXDgq2gqvFJ4JrQm2vQF2tWqgk5N+WJw6V+U8n5Qx6mQbJw1m3m4iS7Zk6m0F1j7oYgU8hXUo1f4V2n2TtGvQWw3mJ9p7wOa2jTtH9h0J+2KkYx5G7EAAAAASUVORK5CYII=',
    "settings": b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAf0lEQVRIie2U0Q2AIBBF3w3i6b2QWl7iQdKqC5pQOaVg6sIuJfQh0p8MEX1Y0qYB+g1lX2f0jTqkE0m5l8f3gQn2m0V5W5oGmKx7Cq0QG3g3zq8pJrZl2z6mS+uQvJcQ5lTtflmYp9g2QZ9G2nV2A9Y5b3gX2vQy7m9gP0j3F6hd0k2gAAAABJRU5ErkJggg==',
    "theme": b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAaElEQVRIie2UsQ2AIBBF3yQkb5vZEUx7E1EJf1Y0Dgq2gqtFJ4JrQm2nQF2tWqgk5N+WJw6V+U8n5Qx6mQbJw1m3m4iS7Zk6m0F1j7oYgU8hXUo1f4V2n2TtGvQWw3mJ9p7wOa2jTtH9h0J+2KkYx5G7EAAAAASUVORK5CYII=',
    "open": b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAcUlEQVRIie2U0Q2AIBBF3xJHfZ4yQyx7E1EJb2UwDgq2gqsFJ4JrQm2nQF2tWqgk5N+WJw6V+U8n5Qx6mQbJw1m3m4iS7Zk6m0F1j7oYgU8hXUo1f4V2n2TtGvQWw3mJ9p7wOa2jTtH9h0J+2KkYx5G7EAAAAASUVORK5CYII=',
    "save": b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAb0lEQVRIie2U0Q2AIBBF3w3i6b2QWl7iQdKqC5pQOaVg6sIuJfQh0p8MEX1Y0qYB+g1lX2f0jTqkE0m5l8f3gQn2m0V5W5oGmKx7Cq0QG3g3zq8pJrZl2z6mS+uQvJcQ5lTtflmYp9g2QZ9G2nV2A9Y5b3gX2vQy7m9gP0j3F6hd0k2gAAAABJRU5ErkJggg==',
    "export": b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAaElEQVRIie2UsQ2AIBBF3yQkb5vZEUx7E1EJf1Y0Dgq2gqtFJ4JrQm2nQF2tWqgk5N+WJw6V+U8n5Qx6mQbJw1m3m4iS7Zk6m0F1j7oYgU8hXUo1f4V2n2TtGvQWw3mJ9p7wOa2jTtH9h0J+2KkYx5G7EAAAAASUVORK5CYII=',
}

def get_icon(name: str, master=None) -> tk.PhotoImage:
    """Return a Tk PhotoImage from base64-encoded PNG."""
    data_b64 = ICON_DATA.get(name) or ICON_DATA["icon"]
    data_str = data_b64.decode("ascii") if isinstance(data_b64, (bytes, bytearray)) else str(data_b64)
    try:
        return tk.PhotoImage(master=master, data=data_str)
    except tk.TclError:
        # Fallback via Pillow if needed
        try:
            from PIL import Image, ImageTk
            import io, base64 as _b64
            raw = _b64.b64decode(data_b64)
            img = Image.open(io.BytesIO(raw))
            return ImageTk.PhotoImage(img, master=master)
        except Exception:
            return tk.PhotoImage(master=master, width=1, height=1)

