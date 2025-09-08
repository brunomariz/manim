from manim import *


class Chunking(Scene):
    def create_grid(self, entries, cell_size):
        n_rows = len(entries)
        n_cols = len(entries[0])
        # Create full grid of squares with text
        grid = VGroup()
        for i in range(n_rows):
            row = VGroup()
            for j in range(n_cols):
                square = Square(side_length=cell_size, color=BLUE)
                number = Text(entries[i][j]).scale(0.5)
                number.move_to(square.get_center())
                row.add(VGroup(square, number))
            row.arrange(RIGHT, buff=0)
            grid.add(row)
        grid.arrange(DOWN, buff=0)
        return grid

    def construct(self):
        entries = [
            ["0", "0", "0", "0", "0", "0", "0", "0"],
            ["0", "1", "1", "1", "1", "1", "1", "0"],
            ["0", "1", "1", "1", "1", "1", "1", "0"],
            ["0", "1", "1", "1", "1", "1", "1", "0"],
            ["0", "1", "1", "1", "1", "1", "1", "0"],
            ["0", "1", "1", "1", "1", "1", "1", "0"],
            ["0", "1", "1", "1", "1", "1", "1", "0"],
            ["0", "0", "0", "0", "0", "0", "0", "0"],
        ]

        cell_size = 0.5
        grid = self.create_grid(entries, cell_size)
        grid.to_edge(LEFT)
        self.play(FadeIn(grid))

        # Split the grid vertically into left and right halves
        n_rows = len(entries)
        n_cols = len(entries[0])
        mid_col = n_cols // 2 + n_cols % 2  # left side +1 if odd

        left_half = VGroup(*[row[:mid_col] for row in grid])
        right_half = VGroup(*[row[mid_col:] for row in grid])

        # Create a box representing the GPU memory
        gpu_square = Rectangle(
            width=cell_size * n_cols * 0.5, height=cell_size * n_rows * 1
        )
        gpu_square.to_edge(RIGHT)
        self.play(Create(gpu_square))

        # Animate fill color for left half
        self.play(
            *[
                cell[0].animate.set_fill(BLUE, opacity=0.5)
                for row in left_half
                for cell in row
            ]
        )

        # Animate fill color for right half
        self.play(
            *[
                cell[0].animate.set_fill(TEAL, opacity=0.5)
                for row in right_half
                for cell in row
            ]
        )

        # **Record original position**
        original_position = left_half.get_center()

        # Move left half inside GPU rectangle
        self.play(left_half.animate.move_to(gpu_square.get_center()))

        # Update left half
        for i, row in enumerate(left_half):
            for j, cell in enumerate(row):
                square, number = cell
                new_value = str(int(entries[i][j]) + 1)  # simple increment
                self.play(
                    Transform(
                        number, Text(new_value).scale(0.5).move_to(square.get_center())
                    ),
                    run_time=0.1,
                )

        # Shift left half back to left side
        self.play(left_half.animate.move_to(original_position))

        self.wait()
