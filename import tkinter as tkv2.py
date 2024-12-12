import tkinter as tk
from tkinter import filedialog

class GlyphEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Éditeur de Glyphes Vectoriels")

        # Gestion des glyphes par lettre
        self.current_letter = tk.StringVar(value="A")
        self.glyphs = {chr(i): [] for i in range(65, 91)}  # Glyphes pour A-Z

        # Canvas pour dessiner
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Boutons pour les outils
        self.tool_frame = tk.Frame(root)
        self.tool_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.current_tool = tk.StringVar(value="point")
        self.add_point_button = tk.Radiobutton(self.tool_frame, text="Ajouter Point", variable=self.current_tool, value="point")
        self.add_point_button.pack(side=tk.LEFT, padx=5)

        self.add_line_button = tk.Radiobutton(self.tool_frame, text="Ajouter Ligne", variable=self.current_tool, value="line")
        self.add_line_button.pack(side=tk.LEFT, padx=5)

        self.add_curve_button = tk.Radiobutton(self.tool_frame, text="Ajouter Courbe", variable=self.current_tool, value="curve")
        self.add_curve_button.pack(side=tk.LEFT, padx=5)

        self.add_fill_button = tk.Radiobutton(self.tool_frame, text="Ajouter Plein", variable=self.current_tool, value="fill")
        self.add_fill_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.tool_frame, text="Sauvegarder", command=self.save_glyphs)
        self.save_button.pack(side=tk.RIGHT, padx=5)

        self.clear_button = tk.Button(self.tool_frame, text="Effacer", command=self.clear_canvas)
        self.clear_button.pack(side=tk.RIGHT, padx=5)

        # Sélecteur de lettre
        self.letter_selector = tk.Frame(root)
        self.letter_selector.pack(side=tk.TOP, fill=tk.X)

        self.prev_letter_button = tk.Button(self.letter_selector, text="<", command=self.prev_letter)
        self.prev_letter_button.pack(side=tk.LEFT, padx=5)

        self.letter_label = tk.Label(self.letter_selector, textvariable=self.current_letter, font=("Arial", 16))
        self.letter_label.pack(side=tk.LEFT, padx=5)

        self.next_letter_button = tk.Button(self.letter_selector, text=">", command=self.next_letter)
        self.next_letter_button.pack(side=tk.LEFT, padx=5)

        # Liste des formes dessinées
        self.shapes = []
        self.current_points = []

        # Événements de la souris
        self.canvas.bind("<Button-1>", self.on_click)

    def prev_letter(self):
        current = ord(self.current_letter.get())
        if current > 65:
            self.save_current_glyph()
            self.current_letter.set(chr(current - 1))
            self.load_current_glyph()

    def next_letter(self):
        current = ord(self.current_letter.get())
        if current < 90:
            self.save_current_glyph()
            self.current_letter.set(chr(current + 1))
            self.load_current_glyph()

    def save_current_glyph(self):
        letter = self.current_letter.get()
        self.glyphs[letter] = [(self.canvas.type(shape), self.canvas.coords(shape)) for shape in self.shapes]

    def load_current_glyph(self):
        self.clear_canvas()
        letter = self.current_letter.get()
        for shape_type, coords in self.glyphs[letter]:
            if shape_type == "line":
                self.shapes.append(self.canvas.create_line(*coords, fill="black"))
            elif shape_type == "oval":
                self.shapes.append(self.canvas.create_oval(*coords, fill="black"))
            elif shape_type == "polygon":
                self.shapes.append(self.canvas.create_polygon(*coords, fill="black"))

    def on_click(self, event):
        tool = self.current_tool.get()

        if tool == "point":
            point = self.canvas.create_oval(event.x - 2, event.y - 2, event.x + 2, event.y + 2, fill="black")
            self.shapes.append(point)
            self.current_points.append((event.x, event.y))

        elif tool == "line" and len(self.current_points) >= 1:
            x1, y1 = self.current_points[-1]
            x2, y2 = event.x, event.y
            line = self.canvas.create_line(x1, y1, x2, y2, fill="black")
            self.shapes.append(line)
            self.current_points.append((x2, y2))

        elif tool == "curve":
            if len(self.current_points) >= 2:
                x1, y1 = self.current_points[-2]
                x2, y2 = self.current_points[-1]
                x3, y3 = event.x, event.y
                curve = self.canvas.create_line(x1, y1, x2, y2, x3, y3, smooth=True, fill="black")
                self.shapes.append(curve)
                self.current_points.append((x3, y3))

        elif tool == "fill" and len(self.current_points) >= 3:
            polygon = self.canvas.create_polygon(*[coord for point in self.current_points for coord in point], fill="black")
            self.shapes.append(polygon)
            self.current_points = []

    def clear_canvas(self):
        self.canvas.delete("all")
        self.shapes = []
        self.current_points = []

    def save_glyphs(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG Files", "*.svg")])
        if file_path:
            with open(file_path, "w") as f:
                f.write(self.generate_svg())

    def generate_svg(self):
        svg_content = ["<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"800\" height=\"600\">"]
        for letter, shapes in self.glyphs.items():
            svg_content.append(f"<!-- Lettre {letter} -->")
            for shape_type, coords in shapes:
                if shape_type == "line":
                    svg_content.append(f"<line x1=\"{coords[0]}\" y1=\"{coords[1]}\" x2=\"{coords[2]}\" y2=\"{coords[3]}\" stroke=\"black\" />")
                elif shape_type == "oval":
                    svg_content.append(f"<circle cx=\"{(coords[0] + coords[2]) / 2}\" cy=\"{(coords[1] + coords[3]) / 2}\" r=\"2\" fill=\"black\" />")
                elif shape_type == "polygon":
                    points = " ".join(f"{x},{y}" for x, y in zip(coords[::2], coords[1::2]))
                    svg_content.append(f"<polygon points=\"{points}\" fill=\"black\" />")
        svg_content.append("</svg>")
        return "\n".join(svg_content)

if __name__ == "__main__":
    root = tk.Tk()
    app = GlyphEditor(root)
    root.mainloop()
