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

        # GPU label
        gpu_label = Text("GPU", font_size=36)
        gpu_label.next_to(gpu_rect, UP, buff=0.2)  # position above the rectangle
        self.play(Create(gpu_rect), Write(gpu_label))

        return gpu_rect

    def update_cell_with_neighbors(
        self, grid, i, j, new_value, duration=0.2, highlight_opacity=0.8
    ):
        """
        Updates grid[i][j] with new_value and temporarily increases the opacity of its neighbors
        """
        n_rows = len(grid)
        n_cols = len(grid[0])
        neighbors = []

        # Collect neighboring cells (up, down, left, right)
        if i > 0:
            neighbors.append(grid[i - 1][j])
        if i < n_rows - 1:
            neighbors.append(grid[i + 1][j])
        if j > 0:
            neighbors.append(grid[i][j - 1])
        if j < n_cols - 1:
            neighbors.append(grid[i][j + 1])

        # Animate neighbor highlight
        highlight_anims = [
            neighbor[0].animate.set_fill(YELLOW, opacity=highlight_opacity)
            for neighbor in neighbors
        ]
        self.play(*highlight_anims, run_time=duration / 2)

        # Update the center cell
        square, number = grid[i][j]
        self.play(
            Transform(number, Text(new_value).scale(0.5).move_to(square.get_center())),
            run_time=duration,
        )

        # Restore neighbor opacity
        restore_anims = [
            neighbor[0].animate.set_fill(BLUE, opacity=0.5) for neighbor in neighbors
        ]
        self.play(*restore_anims, run_time=duration / 2)

    def update_chunk(self, chunk, gpu_rect, entries, index):
        n_cols = len(entries[0])
        mid_col = n_cols // 2 + n_cols % 2
        # Record original positions
        chunk_pos = chunk.get_center()

        # Move chunk to GPU rectangles
        self.play(chunk.animate.move_to(gpu_rect.get_center()))

        # Example: update numbers in left half
        for i, row in enumerate(chunk):
            for j, cell in enumerate(row):
                if index == 0:
                    if not (
                        (i == 0)
                        or (j == 0)
                        or (i == (len(chunk) - 1))
                        or (j == len(chunk[0]) - 1)
                    ):
                        square, number = cell
                        new_value = str(int(number.text) + 1)
                        self.update_cell_with_neighbors(
                            chunk, i, j, new_value, duration=0.2, highlight_opacity=0.2
                        )
                elif index == 1:
                    if not (
                        (i == 0)
                        or (j == 0)
                        or (j == len(chunk[0]) - 1)
                        or (i == (len(chunk) - 1))
                    ):
                        square, number = cell
                        new_value = str(int(number.text) + 1)
                        self.update_cell_with_neighbors(
                            chunk, i, j, new_value, duration=0.2, highlight_opacity=0.2
                        )

        # Move halves back to original positions
        self.play(chunk.animate.move_to(chunk_pos))

    def exchange_halos(self, chunk0: VGroup, chunk1: VGroup, halo_width=1):
        """
        Exchange halo columns between chunk0 and chunk1.
        chunk0: left chunk
        chunk1: right chunk
        halo_width: number of overlapping columns to exchange
        """
        chunk1_pos = chunk1.get_center()

        # Move chunk1 next to chunk0 to visualize exchange
        self.play(chunk1.animate.next_to(chunk0, RIGHT, buff=0.1))

        n_rows = len(chunk0)
        for i in range(n_rows):
            square, number = chunk0[i, -1]
            new_value = str(500)
            self.play(
                Transform(
                    number, Text(new_value).scale(0.5).move_to(square.get_center())
                ),
                run_time=0.2,
            )

        # Move chunk1 back to original position
        self.play(chunk1.animate.move_to(chunk1_pos))

    def construct(self):
        entries = [
            ["0", "0", "0", "0", "0"],
            ["0", "1", "1", "1", "0"],
            ["0", "1", "1", "1", "0"],
            ["0", "1", "1", "1", "0"],
            ["0", "0", "0", "0", "0"],
        ]

        cell_size = 0.5 * len(entries[0]) / 8
        halo_width = 1
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

        self.update_chunk(left_half, gpu_rect, entries, index=0)

        self.wait()

        self.update_chunk(right_half, gpu_rect, entries, index=1)

        self.wait()

        self.exchange_halos(left_half, right_half, halo_width)

        self.wait()
