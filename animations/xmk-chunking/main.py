from manim import *


class Chunking(Scene):
    def create_grid(self, entries, cell_size):
        n_rows = len(entries)
        n_cols = len(entries[0])
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

    def split_grid_into_chunks(self, grid, mid_col, halo_width):
        left_half = VGroup(
            *[
                VGroup(*[cell.copy() for cell in row[: mid_col + halo_width]])
                for row in grid
            ]
        )
        right_half = VGroup(
            *[
                VGroup(*[cell.copy() for cell in row[mid_col - halo_width :]])
                for row in grid
            ]
        )

        # Place halves over the original grid
        left_half.align_to(grid.get_left(), LEFT)
        right_half.align_to(grid.get_right(), RIGHT)

        # Highlight halves
        self.play(
            *[
                cell[0].animate.set_fill(BLUE, opacity=0.25)
                for row in left_half
                for cell in row
            ]
        )
        self.play(
            *[
                cell[0].animate.set_fill(TEAL, opacity=0.25)
                for row in right_half
                for cell in row
            ]
        )

        self.add(left_half, right_half)

        return left_half, right_half

    def create_gpu_rect(self, entries, cell_size, halo_width):
        n_cols = len(entries[0])
        mid_col = n_cols // 2 + n_cols % 2

        padding_x = 0.1
        padding_y = 0.08
        gpu_rect = Rectangle(
            width=(1 + padding_x) * cell_size * (mid_col + halo_width),
            height=(1 + padding_y) * cell_size * len(entries),
        )
        gpu_rect.to_edge(RIGHT, buff=2)
        self.play(Create(gpu_rect))
        return gpu_rect

    def construct(self):
        entries = [
            ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
            ["0", "1", "1", "1", "1", "1", "1", "1", "1", "0"],
            ["0", "1", "1", "1", "1", "1", "1", "1", "1", "0"],
            ["0", "1", "1", "1", "1", "1", "1", "1", "1", "0"],
            ["0", "1", "1", "1", "1", "1", "1", "1", "1", "0"],
            ["0", "1", "1", "1", "1", "1", "1", "1", "1", "0"],
            ["0", "1", "1", "1", "1", "1", "1", "1", "1", "0"],
            ["0", "1", "1", "1", "1", "1", "1", "1", "1", "0"],
            ["0", "1", "1", "1", "1", "1", "1", "1", "1", "0"],
            ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ]

        cell_size = 0.5 * len(entries) / 8
        halo_width = 2
        n_cols = len(entries[0])
        mid_col = n_cols // 2 + n_cols % 2

        grid = self.create_grid(entries, cell_size)
        grid.to_edge(LEFT)
        self.play(FadeIn(grid))

        # GPU rectangle
        gpu_rect = self.create_gpu_rect(entries, cell_size, halo_width)

        # Create **left and right halves with halo copies**
        left_half, right_half = self.split_grid_into_chunks(grid, mid_col, halo_width)

        self.play(FadeOut(grid))

        # Record original positions
        left_pos = left_half.get_center()
        right_pos = right_half.get_center()

        # Move halves to GPU rectangles
        self.play(left_half.animate.move_to(gpu_rect.get_center()))

        # Example: update numbers in left half
        for i, row in enumerate(left_half):
            for j, cell in enumerate(row):
                if (i == 0) or (j == 0) or (i == (len(left_half) - 1)):
                    continue
                else:
                    square, number = cell
                    new_value = str(int(entries[i][min(j, n_cols - 1)]) + 1)
                    self.play(
                        Transform(
                            number,
                            Text(new_value).scale(0.5).move_to(square.get_center()),
                        ),
                        run_time=0.1,
                    )

        # Move halves back to original positions
        self.play(left_half.animate.move_to(left_pos))

        self.wait()
