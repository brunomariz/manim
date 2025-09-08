from manim import *


class Grid:

    def __init__(self, entries, cell_size, fill, opacity):
        self._entries = entries
        self._grid_vgroup = self._create_grid_vgroup(entries, cell_size, fill, opacity)
        self.fill = fill
        self.opacity = opacity

    def _create_grid_vgroup(self, entries, cell_size, fill=None, fill_opacity=1):
        n_rows = len(entries)
        n_cols = len(entries[0])
        grid = VGroup()
        for i in range(n_rows):
            row = VGroup()
            for j in range(n_cols):
                square = Square(side_length=cell_size, color=BLUE)
                square.set_fill(fill, opacity=fill_opacity)
                number = Text(str(entries[i][j])).scale(0.5)
                number.move_to(square.get_center())
                row.add(VGroup(square, number))
            row.arrange(RIGHT, buff=0)
            grid.add(row)
        grid.arrange(DOWN, buff=0)
        return grid

    def get_vgroup(self) -> VGroup:
        return self._grid_vgroup

    def get_entries(self):
        return self._entries

    def set_entry(self, i, j, val: float):
        self._entries[i][j] = val

    def animate_set_entry(self, i, j, val: float):
        self.set_entry(i, j, val)
        square, number = self.get_vgroup()[i][j]
        return Transform(number, Text(str(val)).scale(0.5).move_to(square.get_center()))

    def get_nrows(self):
        return len(self._entries)

    def get_ncols(self):
        return len(self._entries[0])

    def animate_highlight_neighbors(self, i, j):
        neighbors = []

        # Collect neighboring cells (up, down, left, right)
        if i > 0:
            neighbors.append(self.get_vgroup()[i - 1][j])
        if i < self.get_nrows() - 1:
            neighbors.append(self.get_vgroup()[i + 1][j])
        if j > 0:
            neighbors.append(self.get_vgroup()[i][j - 1])
        if j < self.get_ncols() - 1:
            neighbors.append(self.get_vgroup()[i][j + 1])

        # Animate neighbor highlight
        neighbors_colors = [neighbor.get_fill_color() for neighbor in neighbors]
        neighbors_opacities = [neighbor.get_fill_opacity() for neighbor in neighbors]
        highlight_anims = [
            neighbor[0].animate.set_fill(YELLOW, opacity=0.3) for neighbor in neighbors
        ]

        return highlight_anims

    def animate_highlight_entry(self, i, j):
        # Animate highlight
        square, number = self.get_vgroup()[i][j]
        highlight_anim = square.animate.set_fill(YELLOW, opacity=0.3)

        return highlight_anim

    def animate_reset_fill(self):
        anims = []

        for row in self.get_vgroup():
            for cell in row:
                square, _ = cell
                anims.append(square.animate.set_fill(self.fill, self.opacity))

        return anims


class Chunking5p(Scene):
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

        return gpu_rect, gpu_label

    def run_chunks(self, left_chunk: Grid, right_chunk: Grid, gpu_rect: Rectangle):
        # Save chunks position
        left_pos = left_chunk.get_vgroup().get_center()
        # Move chunk to gpu
        anim = left_chunk.get_vgroup().animate.move_to(gpu_rect.get_center())
        self.play(anim, run_time=1)
        x_m = 1
        x_M = left_chunk.get_nrows() - 2
        y_m = 1
        y_M = left_chunk.get_ncols() - 2
        anims = []
        for x in range(x_m, x_M + 1):
            for y in range(y_m, y_M + 1):
                set_entry_anim = left_chunk.animate_set_entry(
                    x, y, left_chunk.get_entries()[x][y] + 1
                )
                if x * left_chunk.get_ncols() + y < 5 + left_chunk.get_ncols():
                    highlight_anim = left_chunk.animate_highlight_neighbors(x, y)
                    self.play(highlight_anim, set_entry_anim, run_time=0.2)
                    anim = left_chunk.animate_reset_fill()
                    self.play(anim, run_time=0.2)
                    self.play(set_entry_anim, run_time=0.2)
                else:
                    anims.append(set_entry_anim)
        self.play(*anims, run_time=1)
        # Restore chunks position
        self.play(left_chunk.get_vgroup().animate.move_to(left_pos), run_time=1)

        # Save chunks position
        right_pos = right_chunk.get_vgroup().get_center()
        # Move chunk to gpu
        anim = right_chunk.get_vgroup().animate.move_to(gpu_rect.get_center())
        self.play(anim, run_time=1)
        x_m = 1
        x_M = right_chunk.get_nrows() - 2
        y_m = 1
        y_M = right_chunk.get_ncols() - 2
        anims = []
        for x in range(x_m, x_M + 1):
            for y in range(y_m, y_M + 1):
                set_entry_anim = right_chunk.animate_set_entry(
                    x, y, right_chunk.get_entries()[x][y] + 1
                )
                if x * right_chunk.get_ncols() + y < 5 + right_chunk.get_ncols():
                    highlight_anim = right_chunk.animate_highlight_neighbors(x, y)
                    self.play(highlight_anim, set_entry_anim, run_time=0.2)
                    anim = right_chunk.animate_reset_fill()
                    self.play(anim, run_time=0.2)
                    self.play(set_entry_anim, run_time=0.2)
                else:
                    anims.append(set_entry_anim)
        self.play(*anims, run_time=1)
        # Restore chunks position
        self.play(right_chunk.get_vgroup().animate.move_to(right_pos), run_time=1)

    def exchange_halos(self, left_chunk: Grid, right_chunk: Grid):
        right_pos = right_chunk.get_vgroup().get_center()
        self.play(right_chunk.get_vgroup().animate.next_to(left_chunk.get_vgroup()))
        x_m = 0
        x_M = left_chunk.get_nrows() - 1
        y_m = left_chunk.get_ncols() - 1
        y_M = left_chunk.get_ncols() - 1
        for x in range(x_m, x_M + 1):
            for y in range(y_m, y_M + 1):
                y_right = y - 2
                set_entry_anim = left_chunk.animate_set_entry(
                    x, y, right_chunk.get_entries()[x][y_right]
                )
                halo_data_anim = right_chunk.animate_highlight_entry(x, y_right)

                self.play(set_entry_anim, halo_data_anim, run_time=0.2)
        x_m = 0
        x_M = left_chunk.get_nrows() - 1
        y_m = 0
        y_M = 0
        for x in range(x_m, x_M + 1):
            for y in range(y_m, y_M + 1):
                y_left = y + 2
                set_entry_anim = right_chunk.animate_set_entry(
                    x, y, left_chunk.get_entries()[x][y_left]
                )
                halo_data_anim = left_chunk.animate_highlight_entry(x, y_left)

                self.play(set_entry_anim, halo_data_anim, run_time=0.2)

        self.play(right_chunk.get_vgroup().animate.move_to(right_pos))

    def construct(self):
        initial_entries = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]
        cell_size = 0.5

        grid = Grid(initial_entries, cell_size, None, 0)

        mid_col = grid.get_ncols() // 2 + grid.get_ncols() % 2
        halo_width = 1
        left_chunk = Grid(
            [
                entry
                for entry in [row[: mid_col + halo_width] for row in grid.get_entries()]
            ],
            cell_size,
            fill=BLUE,
            opacity=0.2,
        )
        right_chunk = Grid(
            [
                entry
                for entry in [row[mid_col - halo_width :] for row in grid.get_entries()]
            ],
            cell_size,
            fill=GREEN,
            opacity=0.2,
        )

        grid.get_vgroup().to_edge(LEFT)

        left_chunk.get_vgroup().align_to(grid.get_vgroup().get_left(), LEFT)
        right_chunk.get_vgroup().align_to(grid.get_vgroup().get_right(), RIGHT)

        cpu_label = Text("CPU")
        cpu_label.next_to(grid.get_vgroup(), UP)

        self.play(FadeIn(grid.get_vgroup()), FadeIn(cpu_label))

        gpu_rect, gpu_label = self.create_gpu_rect(
            grid.get_entries(), cell_size, halo_width
        )
        self.play(Create(gpu_rect), Write(gpu_label))

        self.play(FadeIn(left_chunk.get_vgroup()))
        self.play(FadeIn(right_chunk.get_vgroup()))
        self.play(FadeOut(grid.get_vgroup()))

        self.run_chunks(left_chunk, right_chunk, gpu_rect)
        self.exchange_halos(left_chunk, right_chunk)

        self.run_chunks(left_chunk, right_chunk, gpu_rect)
        self.exchange_halos(left_chunk, right_chunk)

        self.run_chunks(left_chunk, right_chunk, gpu_rect)
        self.exchange_halos(left_chunk, right_chunk)

        self.run_chunks(left_chunk, right_chunk, gpu_rect)
        self.exchange_halos(left_chunk, right_chunk)

        self.wait()


class Chunking5pBlocking(Scene):
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

        return gpu_rect, gpu_label

    def run_chunks_temporal_blocking(
        self,
        left_chunk: Grid,
        right_chunk: Grid,
        gpu_rect: Rectangle,
        temporal_blocking,
    ):
        # Save chunk position
        left_pos = left_chunk.get_vgroup().get_center()
        # Move left chunk to gpu
        anim = left_chunk.get_vgroup().animate.move_to(gpu_rect.get_center())
        self.play(anim, run_time=1)

        for t_blk in range(temporal_blocking):
            x_m = 1
            x_M = left_chunk.get_nrows() - 2
            y_m = 1
            y_M = left_chunk.get_ncols() - 2 - t_blk
            anims = []
            for x in range(x_m, x_M + 1):
                for y in range(y_m, y_M + 1):
                    set_entry_anim = left_chunk.animate_set_entry(
                        x, y, left_chunk.get_entries()[x][y] + 1
                    )
                    if x * left_chunk.get_ncols() + y < 5 + left_chunk.get_ncols():
                        highlight_anim = left_chunk.animate_highlight_neighbors(x, y)
                        self.play(highlight_anim, set_entry_anim, run_time=0.2)
                        anim = left_chunk.animate_reset_fill()
                        self.play(anim, run_time=0.2)
                        self.play(set_entry_anim, run_time=0.2)
                    else:
                        anims.append(set_entry_anim)
            self.play(*anims, run_time=1)
        # Return chunks position
        self.play(left_chunk.get_vgroup().animate.move_to(left_pos), run_time=1)

        # Save chunks position
        right_pos = right_chunk.get_vgroup().get_center()
        # Move chunk to gpu
        anim = right_chunk.get_vgroup().animate.move_to(gpu_rect.get_center())
        self.play(anim, run_time=1)

        for t_blk in range(temporal_blocking):
            x_m = 1
            x_M = right_chunk.get_nrows() - 2
            y_m = 1 + t_blk
            y_M = right_chunk.get_ncols() - 2
            anims = []
            for x in range(x_m, x_M + 1):
                for y in range(y_m, y_M + 1):
                    set_entry_anim = right_chunk.animate_set_entry(
                        x, y, right_chunk.get_entries()[x][y] + 1
                    )
                    if x * right_chunk.get_ncols() + y < 5 + right_chunk.get_ncols():
                        highlight_anim = right_chunk.animate_highlight_neighbors(x, y)
                        self.play(highlight_anim, set_entry_anim, run_time=0.2)
                        anim = right_chunk.animate_reset_fill()
                        self.play(anim, run_time=0.2)
                        self.play(set_entry_anim, run_time=0.2)
                    else:
                        anims.append(set_entry_anim)
            self.play(*anims, run_time=1)
        # Restore chunks position
        self.play(right_chunk.get_vgroup().animate.move_to(right_pos), run_time=1)

    def exchange_halos(self, left_chunk: Grid, right_chunk: Grid, temporal_blocking):
        right_pos = right_chunk.get_vgroup().get_center()
        self.play(right_chunk.get_vgroup().animate.next_to(left_chunk.get_vgroup()))

        x_m = 0
        x_M = left_chunk.get_nrows() - 1
        y_m = left_chunk.get_ncols() - temporal_blocking
        y_M = left_chunk.get_ncols() - 1
        for x in range(x_m, x_M + 1):
            for y in range(y_m, y_M + 1):
                y_right = y - 2
                set_entry_anim = left_chunk.animate_set_entry(
                    x, y, right_chunk.get_entries()[x][y_right]
                )
                halo_data_anim = right_chunk.animate_highlight_entry(x, y_right)

                self.play(set_entry_anim, halo_data_anim, run_time=0.2)
        x_m = 0
        x_M = left_chunk.get_nrows() - 1
        y_m = 0
        y_M = temporal_blocking - 1
        for x in range(x_m, x_M + 1):
            for y in range(y_m, y_M + 1):
                y_left = y + 2
                set_entry_anim = right_chunk.animate_set_entry(
                    x, y, left_chunk.get_entries()[x][y_left]
                )
                halo_data_anim = left_chunk.animate_highlight_entry(x, y_left)

                self.play(set_entry_anim, halo_data_anim, run_time=0.2)

        self.play(right_chunk.get_vgroup().animate.move_to(right_pos))

    def construct(self):
        initial_entries = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]
        cell_size = 0.5

        grid = Grid(initial_entries, cell_size, None, 0)

        mid_col = grid.get_ncols() // 2 + grid.get_ncols() % 2
        temporal_blocking = 2
        temporal_blocking_halo = temporal_blocking - 1
        halo_width = 1
        left_chunk = Grid(
            [
                entry
                for entry in [
                    row[: mid_col + halo_width + temporal_blocking_halo]
                    for row in grid.get_entries()
                ]
            ],
            cell_size,
            fill=BLUE,
            opacity=0.2,
        )
        right_chunk = Grid(
            [
                entry
                for entry in [
                    row[mid_col - halo_width - temporal_blocking_halo :]
                    for row in grid.get_entries()
                ]
            ],
            cell_size,
            fill=GREEN,
            opacity=0.2,
        )

        grid.get_vgroup().to_edge(LEFT)

        left_chunk.get_vgroup().align_to(grid.get_vgroup().get_left(), LEFT)
        right_chunk.get_vgroup().align_to(grid.get_vgroup().get_right(), RIGHT)

        cpu_label = Text("CPU")
        cpu_label.next_to(grid.get_vgroup(), UP)

        self.play(FadeIn(grid.get_vgroup()), FadeIn(cpu_label))

        gpu_rect, gpu_label = self.create_gpu_rect(
            grid.get_entries(), cell_size, halo_width + temporal_blocking_halo
        )
        self.play(Create(gpu_rect), Write(gpu_label))

        self.play(FadeIn(left_chunk.get_vgroup()))
        self.play(FadeIn(right_chunk.get_vgroup()))
        self.play(FadeOut(grid.get_vgroup()))

        self.run_chunks_temporal_blocking(
            left_chunk, right_chunk, gpu_rect, temporal_blocking
        )
        self.exchange_halos(left_chunk, right_chunk, temporal_blocking)

        self.run_chunks_temporal_blocking(
            left_chunk, right_chunk, gpu_rect, temporal_blocking
        )
        self.exchange_halos(left_chunk, right_chunk, temporal_blocking)

        self.wait()
